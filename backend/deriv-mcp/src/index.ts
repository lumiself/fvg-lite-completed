#!/usr/bin/env node
/**
 * Deriv MCP Server v2.0.0
 * 
 * Comprehensive Deriv API integration for trading data, account management,
 * and market analysis. This server provides access to:
 * 
 * - Real-time market data (ticks, candles, symbols)
 * - Trading operations (buy/sell contracts)
 * - Account information (balance, portfolio, statement)
 * - Market analysis tools
 * 
 * API Documentation: https://api.deriv.com/
 * WebSocket Documentation: https://api.deriv.com/websockets
 * 
 * Environment Variables:
 * - DERIV_APP_ID: Your Deriv app ID (default: 1089)
 * - DERIV_API_TOKEN: Your Deriv API token (optional)
 * 
 * Rate Limits:
 * - 120 requests per minute for public endpoints
 * - 60 requests per minute for authenticated endpoints
 * 
 * Supported Markets:
 * - forex: Currency pairs (EUR/USD, GBP/USD, etc.)
 * - synthetic_index: Volatility indices (R_50, R_100, etc.)
 * - commodities: Gold, Silver, Oil
 * - indices: Stock indices (US_30, US_100, etc.)
 * - crypto: Cryptocurrency pairs
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import axios from 'axios';

// Configuration
const DERIV_APP_ID = process.env.DERIV_APP_ID || '1089';
const DERIV_API_TOKEN = process.env.DERIV_API_TOKEN || '';

// API Endpoints
const WS_URL = `wss://ws.derivws.com/websockets/v3?app_id=${DERIV_APP_ID}`;
const REST_URL = 'https://api.deriv.com/api';

// Interfaces for Deriv API responses
interface DerivCandle {
  epoch: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

interface DerivSymbol {
  symbol: string;
  display_name: string;
  market: string;
  market_display_name: string;
  pip: number;
  contract_category: string;
  exchange_is_open: number;
}

interface DerivTick {
  ask: number;
  bid: number;
  epoch: number;
  pip_size: number;
  quote: number;
  symbol: string;
}

interface DerivContract {
  contract_id: string;
  contract_type: string;
  currency: string;
  date_start: number;
  date_expiry: number;
  entry_tick: number;
  entry_tick_time: number;
  exit_tick: number;
  exit_tick_time: number;
  barrier: string;
  buy_price: number;
  payout: number;
  profit: number;
  shortcode: string;
  transaction_id: string;
}

interface DerivAccount {
  balance: number;
  currency: string;
  loginid: string;
}

class DerivMCPServer {
  private server: Server;
  private axiosInstance;

  constructor() {
    this.server = new Server(
      {
        name: 'deriv-mcp-server',
        version: '2.0.0',
        description: 'Comprehensive Deriv API integration for trading data, account management, and market analysis',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.axiosInstance = axios.create({
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupToolHandlers();
    
    // Error handling
    this.server.onerror = (error: any) => console.error('[MCP Error]', error);
    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  private setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'get_active_symbols',
          description: 'Get list of active trading symbols from Deriv with detailed market information',
          inputSchema: {
            type: 'object',
            properties: {
              market: {
                type: 'string',
                description: 'Market type: forex, synthetic_index, commodities, indices, crypto',
              },
              landing_company: {
                type: 'string',
                description: 'Landing company (svg, malta, etc.)',
                default: 'svg',
              },
            },
          },
        },
        {
          name: 'get_historical_candles',
          description: 'Get historical candlestick data for a symbol with OHLCV format',
          inputSchema: {
            type: 'object',
            properties: {
              symbol: {
                type: 'string',
                description: 'Trading symbol (e.g., frxEURUSD, R_50, cryBTCUSD)',
              },
              timeframe: {
                type: 'number',
                description: 'Timeframe in seconds: 60(1m), 300(5m), 900(15m), 1800(30m), 3600(1h), 14400(4h), 86400(1d)',
                default: 3600,
              },
              count: {
                type: 'number',
                description: 'Number of candles (1-1000)',
                default: 100,
                minimum: 1,
                maximum: 1000,
              },
              end_time: {
                type: 'number',
                description: 'End time in epoch seconds (optional)',
              },
              start_time: {
                type: 'number',
                description: 'Start time in epoch seconds (optional)',
              },
            },
            required: ['symbol'],
          },
        },
        {
          name: 'get_tick_data',
          description: 'Get latest tick data with bid/ask/quote prices',
          inputSchema: {
            type: 'object',
            properties: {
              symbol: {
                type: 'string',
                description: 'Trading symbol',
              },
              count: {
                type: 'number',
                description: 'Number of ticks (1-100)',
                default: 1,
                minimum: 1,
                maximum: 100,
              },
              subscribe: {
                type: 'boolean',
                description: 'Subscribe to real-time ticks',
                default: false,
              },
            },
            required: ['symbol'],
          },
        },
        {
          name: 'get_trading_times',
          description: 'Get trading times for symbols and markets',
          inputSchema: {
            type: 'object',
            properties: {
              symbols: {
                type: 'array',
                items: { type: 'string' },
                description: 'List of symbols to check',
              },
            },
          },
        },
        {
          name: 'get_contracts_for_symbol',
          description: 'Get available contract types for a symbol',
          inputSchema: {
            type: 'object',
            properties: {
              symbol: {
                type: 'string',
                description: 'Trading symbol',
              },
            },
            required: ['symbol'],
          },
        },
        {
          name: 'get_account_balance',
          description: 'Get account balance and currency information (requires API token)',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
        {
          name: 'get_portfolio',
          description: 'Get open positions and portfolio (requires API token)',
          inputSchema: {
            type: 'object',
            properties: {
              contract_type: {
                type: 'string',
                description: 'Filter by contract type (optional)',
              },
            },
          },
        },
        {
          name: 'get_statement',
          description: 'Get account statement with transactions (requires API token)',
          inputSchema: {
            type: 'object',
            properties: {
              limit: {
                type: 'number',
                description: 'Number of transactions (1-100)',
                default: 50,
                minimum: 1,
                maximum: 100,
              },
              offset: {
                type: 'number',
                description: 'Offset for pagination',
                default: 0,
              },
              date_from: {
                type: 'string',
                description: 'Start date (YYYY-MM-DD)',
              },
              date_to: {
                type: 'string',
                description: 'End date (YYYY-MM-DD)',
              },
            },
          },
        },
        {
          name: 'buy_contract',
          description: 'Buy a trading contract (requires API token)',
          inputSchema: {
            type: 'object',
            properties: {
              symbol: {
                type: 'string',
                description: 'Trading symbol',
              },
              contract_type: {
                type: 'string',
                description: 'Contract type: CALL, PUT, ASIAN, DIGITMATCH, etc.',
              },
              duration: {
                type: 'number',
                description: 'Contract duration in seconds',
              },
              duration_unit: {
                type: 'string',
                description: 'Duration unit: s, m, h, d',
                default: 's',
              },
              amount: {
                type: 'number',
                description: 'Stake amount',
              },
              basis: {
                type: 'string',
                description: 'Basis: stake, payout',
                default: 'stake',
              },
              barrier: {
                type: 'string',
                description: 'Barrier for contracts (optional)',
              },
            },
            required: ['symbol', 'contract_type', 'duration', 'amount'],
          },
        },
        {
          name: 'sell_contract',
          description: 'Sell/close a position (requires API token)',
          inputSchema: {
            type: 'object',
            properties: {
              contract_id: {
                type: 'string',
                description: 'Contract ID to sell',
              },
            },
            required: ['contract_id'],
          },
        },
        {
          name: 'test_connection',
          description: 'Test connection to Deriv API and get server status',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
        {
          name: 'get_server_time',
          description: 'Get current server time in epoch format',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request: any) => {
      try {
        switch (request.params.name) {
          case 'get_active_symbols':
            return await this.getActiveSymbols(request.params.arguments || {});
          
          case 'get_historical_candles':
            return await this.getHistoricalCandles(request.params.arguments || {});
          
          case 'get_tick_data':
            return await this.getTickData(request.params.arguments || {});
          
          case 'get_trading_times':
            return await this.getTradingTimes(request.params.arguments || {});
          
          case 'get_contracts_for_symbol':
            return await this.getContractsForSymbol(request.params.arguments || {});
          
          case 'get_account_balance':
            return await this.getAccountBalance();
          
          case 'get_portfolio':
            return await this.getPortfolio(request.params.arguments || {});
          
          case 'get_statement':
            return await this.getStatement(request.params.arguments || {});
          
          case 'buy_contract':
            return await this.buyContract(request.params.arguments || {});
          
          case 'sell_contract':
            return await this.sellContract(request.params.arguments || {});
          
          case 'test_connection':
            return await this.testConnection();
          
          case 'get_server_time':
            return await this.getServerTime();
          
          default:
            throw new McpError(
              ErrorCode.MethodNotFound,
              `Unknown tool: ${request.params.name}`
            );
        }
      } catch (error) {
        if (error instanceof McpError) {
          throw error;
        }
        
        return {
          content: [
            {
              type: 'text',
              text: `Error: ${error instanceof Error ? error.message : String(error)}`,
            },
          ],
          isError: true,
        };
      }
    });
  }

  private async makeApiRequest(payload: any) {
    try {
      const response = await this.axiosInstance.post(WS_URL, payload);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(`API request failed: ${error.response?.data?.error?.message || error.message}`);
      }
      throw error;
    }
  }

  private async getActiveSymbols(args: any) {
    const payload = {
      active_symbols: "brief",
      product_type: "basic",
      ...(args.landing_company && { landing_company: args.landing_company })
    };

    const data = await this.makeApiRequest(payload);
    
    if (data.error) {
      throw new Error(`Deriv API error: ${data.error.message}`);
    }

    let symbols = data.active_symbols || [];
    
    if (args.market) {
      symbols = symbols.filter((s: DerivSymbol) => s.market === args.market);
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            symbols: symbols,
            count: symbols.length,
            markets: [...new Set(symbols.map((s: DerivSymbol) => s.market))],
            timestamp: Date.now()
          }, null, 2),
        },
      ],
    };
  }

  private async getHistoricalCandles(args: any) {
    const { symbol, timeframe = 3600, count = 100, start_time, end_time } = args;

    const payload: any = {
      candles: 1,
      symbol,
      granularity: timeframe,
      count: Math.min(count, 1000),
      style: "candles"
    };

    if (start_time) payload.start = start_time;
    if (end_time) payload.end = end_time;

    const data = await this.makeApiRequest(payload);

    if (data.error) {
      throw new Error(`Deriv API error: ${data.error.message}`);
    }

    const candles = data.candles || [];

    const normalizedCandles = candles.map((candle: any) => ({
      timestamp: candle.epoch,
      datetime: new Date(candle.epoch * 1000).toISOString(),
      open: parseFloat(candle.open),
      high: parseFloat(candle.high),
      low: parseFloat(candle.low),
      close: parseFloat(candle.close),
      volume: parseInt(candle.volume || '0'),
      symbol: symbol
    }));

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            candles: normalizedCandles,
            symbol: symbol,
            timeframe: timeframe,
            count: normalizedCandles.length,
            period: {
              start: normalizedCandles[0]?.datetime,
              end: normalizedCandles[normalizedCandles.length - 1]?.datetime
            }
          }, null, 2),
        },
      ],
    };
  }

  private async getTickData(args: any) {
    const { symbol, count = 1, subscribe = false } = args;

    const payload = {
      ticks: symbol,
      subscribe: subscribe ? 1 : 0,
      count: Math.min(count, 100)
    };

    const data = await this.makeApiRequest(payload);

    if (data.error) {
      throw new Error(`Deriv API error: ${data.error.message}`);
    }

    const ticks = data.history || [data.tick] || [];

    const normalizedTicks = ticks.map((tick: any) => ({
      timestamp: tick.epoch,
      datetime: new Date(tick.epoch * 1000).toISOString(),
      symbol: tick.symbol,
      bid: parseFloat(tick.bid),
      ask: parseFloat(tick.ask),
      quote: parseFloat(tick.quote),
      pip_size: tick.pip_size
    }));

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            ticks: normalizedTicks,
            symbol: symbol,
            count: normalizedTicks.length,
            latest: normalizedTicks[normalizedTicks.length - 1]
          }, null, 2),
        },
      ],
    };
  }

  private async getTradingTimes(args: any) {
    const payload: any = {
      trading_times: 1
    };

    if (args.symbols && Array.isArray(args.symbols)) {
      payload.symbols = args.symbols;
    }

    const data = await this.makeApiRequest(payload);

    if (data.error) {
      throw new Error(`Deriv API error: ${data.error.message}`);
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(data, null, 2),
        },
      ],
    };
  }

  private async getContractsForSymbol(args: any) {
    const { symbol } = args;

    const payload = {
      contracts_for: symbol
    };

    const data = await this.makeApiRequest(payload);

    if (data.error) {
      throw new Error(`Deriv API error: ${data.error.message}`);
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(data, null, 2),
        },
      ],
    };
  }

  private async getAccountBalance() {
    if (!DERIV_API_TOKEN) {
      throw new Error('API token required for account operations');
    }

    const payload = {
      authorize: DERIV_API_TOKEN
    };

    const authData = await this.makeApiRequest(payload);
    
    if (authData.error) {
      throw new Error(`Authorization failed: ${authData.error.message}`);
    }

    const balancePayload = {
      balance: 1
    };

    const data = await this.makeApiRequest(balancePayload);

    if (data.error) {
      throw new Error(`Deriv API error: ${data.error.message}`);
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            balance: data.balance,
            currency: data.currency,
            loginid: data.loginid,
            timestamp: Date.now()
          }, null, 2),
        },
      ],
    };
  }

  private async getPortfolio(args: any) {
    if (!DERIV_API_TOKEN) {
      throw new Error('API token required for account operations');
    }

    const payload = {
      authorize: DERIV_API_TOKEN
    };

    await this.makeApiRequest(payload);

    const portfolioPayload = {
      portfolio: 1
    };

    const data = await this.makeApiRequest(portfolioPayload);

    if (data.error) {
      throw new Error(`Deriv API error: ${data.error.message}`);
    }

    let contracts = data.portfolio?.contracts || [];
    
    if (args.contract_type) {
      contracts = contracts.filter((c: any) => c.contract_type === args.contract_type);
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            contracts: contracts,
            total_count: contracts.length,
            total_value: contracts.reduce((sum: number, c: any) => sum + (c.buy_price || 0), 0)
          }, null, 2),
        },
      ],
    };
  }

  private async getStatement(args: any) {
    if (!DERIV_API_TOKEN) {
      throw new Error('API token required for account operations');
    }

    const { limit = 50, offset = 0, date_from, date_to } = args;

    const payload = {
      authorize: DERIV_API_TOKEN
    };

    await this.makeApiRequest(payload);

    const statementPayload: any = {
      statement: 1,
      limit: Math.min(limit, 100),
      offset: offset
    };

    if (date_from) statementPayload.date_from = date_from;
    if (date_to) statementPayload.date_to = date_to;

    const data = await this.makeApiRequest(statementPayload);

    if (data.error) {
      throw new Error(`Deriv API error: ${data.error.message}`);
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            transactions: data.statement?.transactions || [],
            count: data.statement?.count || 0,
            total_deposits: data.statement?.total_deposits || 0,
            total_withdrawals: data.statement?.total_withdrawals || 0,
            total_turnover: data.statement?.total_turnover || 0
          }, null, 2),
        },
      ],
    };
  }

  private async buyContract(args: any) {
    if (!DERIV_API_TOKEN) {
      throw new Error('API token required for trading operations');
    }

    const { symbol, contract_type, duration, amount, duration_unit = 's', basis = 'stake', barrier } = args;

    const authPayload = {
      authorize: DERIV_API_TOKEN
    };

    await this.makeApiRequest(authPayload);

    const buyPayload: any = {
      buy: 1,
      price: amount,
      parameters: {
        amount: amount,
        basis: basis,
        contract_type: contract_type,
        currency: 'USD',
        duration: duration,
        duration_unit: duration_unit,
        symbol: symbol
      }
    };

    if (barrier) {
      buyPayload.parameters.barrier = barrier;
    }

    const data = await this.makeApiRequest(buyPayload);

    if (data.error) {
      throw new Error(`Deriv API error: ${data.error.message}`);
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            contract_id: data.buy?.contract_id,
            longcode: data.buy?.longcode,
            transaction_id: data.buy?.transaction_id,
            buy_price: data.buy?.buy_price,
            payout: data.buy?.payout,
            start_time: data.buy?.start_time,
            expiry_time: data.buy?.expiry_time,
            symbol: symbol,
            contract_type: contract_type
          }, null, 2),
        },
      ],
    };
  }

  private async sellContract(args: any) {
    if (!DERIV_API_TOKEN) {
      throw new Error('API token required for trading operations');
    }

    const { contract_id } = args;

    const authPayload = {
      authorize: DERIV_API_TOKEN
    };

    await this.makeApiRequest(authPayload);

    const sellPayload = {
      sell: contract_id
    };

    const data = await this.makeApiRequest(sellPayload);

    if (data.error) {
      throw new Error(`Deriv API error: ${data.error.message}`);
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            contract_id: contract_id,
            sold_for: data.sell?.sold_for,
            transaction_id: data.sell?.transaction_id,
            profit: data.sell?.sold_for - (data.sell?.buy_price || 0)
          }, null, 2),
        },
      ],
    };
  }

  private async testConnection() {
    const payload = {
      ping: 1
    };

    try {
      const data = await this.makeApiRequest(payload);

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              success: true,
              message: 'Successfully connected to Deriv API',
              app_id: DERIV_APP_ID,
              api_token_configured: !!DERIV_API_TOKEN,
              server_time: data.ping,
              websocket_url: WS_URL,
              documentation: 'https://api.deriv.com/',
              supported_endpoints: [
                'active_symbols',
                'candles',
                'ticks',
                'trading_times',
                'contracts_for',
                'balance',
                'portfolio',
                'statement',
                'buy',
                'sell'
              ],
              rate_limits: {
                public: '120 requests/minute',
                authenticated: '60 requests/minute'
              }
            }, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              success: false,
              error: error instanceof Error ? error.message : String(error),
              troubleshooting: {
                check_app_id: 'Verify DERIV_APP_ID is valid',
                check_network: 'Ensure internet connection',
                check_url: 'Confirm websocket URL format',
                documentation: 'https://api.deriv.com/docs/'
              }
            }, null, 2),
          },
        ],
        isError: true,
      };
    }
  }

  private async getServerTime() {
    const payload = {
      time: 1
    };

    const data = await this.makeApiRequest(payload);

    if (data.error) {
      throw new Error(`Deriv API error: ${data.error.message}`);
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            epoch: data.time,
            datetime: new Date(data.time * 1000).toISOString(),
            timezone: 'UTC'
          }, null, 2),
        },
      ],
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Deriv MCP server v2.0.0 running with comprehensive API documentation');
  }
}

const server = new DerivMCPServer();
server.run().catch(console.error);
