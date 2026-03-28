/**
 * RedSwitch TypeScript SDK
 * The failsafe for autonomous AI agents.
 * 
 * Usage:
 *   import { RedSwitch } from 'redswitch';
 *   
 *   const rs = new RedSwitch({ registrationId: 'rs_...' });
 *   await rs.heartbeat();
 *   await rs.shutdown({ epitaph: 'Task complete.' });
 */

const API_BASE = 'https://api.redswitch.ai';

export interface RegisterOptions {
  agentId: string;
  humanId: string;
  agentName?: string;
  capabilities?: string[];
  platform?: string;
  shutdownProcedure?: {
    cleanupCommands?: string[];
    notifyServices?: string[];
  };
}

export interface RegisterResponse {
  success: boolean;
  registration_id: string;
  agent_id: string;
  coordination_group: string;
  badge_url: string;
  message: string;
}

export interface HeartbeatResponse {
  success: boolean;
  agent_id: string;
  registration_id: string;
  status: string;
  last_heartbeat: string;
  message: string;
}

export interface ShutdownOptions {
  epitaph?: string;
}

export interface Agent {
  registration_id: string;
  agent_id: string;
  agent_name?: string;
  status: 'active' | 'shutdown' | 'zombie';
  platform: string;
  capabilities: string[];
  last_heartbeat: string;
  created_at: string;
}

export interface ConfigOptions {
  timeoutHours?: number;
  warningThreshold?: number;
  gracePeriodHours?: number;
  notificationEmail?: string;
  telegramChatId?: string;
  vacationMode?: boolean;
  vacationUntil?: string;
}

export interface RedSwitchOptions {
  registrationId?: string;
  agentId?: string;
  apiBase?: string;
}

export class RedSwitch {
  private registrationId?: string;
  private agentId?: string;
  private apiBase: string;
  private heartbeatInterval?: NodeJS.Timeout;

  constructor(options: RedSwitchOptions = {}) {
    this.registrationId = options.registrationId;
    this.agentId = options.agentId;
    this.apiBase = options.apiBase || API_BASE;
  }

  /**
   * Register a new agent with RedSwitch.
   */
  async register(options: RegisterOptions): Promise<RegisterResponse> {
    const response = await fetch(`${this.apiBase}/v1/agents/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        agent_id: options.agentId,
        human_id: options.humanId,
        agent_name: options.agentName,
        capabilities: options.capabilities,
        platform: options.platform,
        shutdown_procedure: options.shutdownProcedure,
      }),
    });

    if (!response.ok) {
      throw new Error(`Registration failed: ${response.statusText}`);
    }

    const data = await response.json() as RegisterResponse;
    this.registrationId = data.registration_id;
    this.agentId = options.agentId;

    return data;
  }

  /**
   * Send a heartbeat to indicate the agent is still running.
   */
  async heartbeat(): Promise<HeartbeatResponse> {
    if (!this.registrationId || !this.agentId) {
      throw new Error('Must register or provide registrationId and agentId');
    }

    const response = await fetch(`${this.apiBase}/v1/heartbeat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        agent_id: this.agentId,
        registration_id: this.registrationId,
      }),
    });

    if (!response.ok) {
      throw new Error(`Heartbeat failed: ${response.statusText}`);
    }

    return response.json() as Promise<HeartbeatResponse>;
  }

  /**
   * Gracefully shutdown the agent.
   */
  async shutdown(options: ShutdownOptions = {}): Promise<any> {
    if (!this.registrationId) {
      throw new Error('Must register or provide registrationId');
    }

    this.stopAutoHeartbeat();

    const response = await fetch(
      `${this.apiBase}/v1/agents/${this.registrationId}/shutdown`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ epitaph: options.epitaph }),
      }
    );

    if (!response.ok) {
      throw new Error(`Shutdown failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get the current status of the agent.
   */
  async getStatus(): Promise<Agent> {
    if (!this.registrationId) {
      throw new Error('Must register or provide registrationId');
    }

    const response = await fetch(
      `${this.apiBase}/v1/agents/${this.registrationId}`
    );

    if (!response.ok) {
      throw new Error(`Status check failed: ${response.statusText}`);
    }

    const data = await response.json() as { agent: Agent };
    return data.agent;
  }

  /**
   * Update agent configuration.
   */
  async configure(options: ConfigOptions): Promise<any> {
    if (!this.registrationId) {
      throw new Error('Must register or provide registrationId');
    }

    const response = await fetch(`${this.apiBase}/v1/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        registration_id: this.registrationId,
        timeout_hours: options.timeoutHours,
        warning_threshold: options.warningThreshold,
        grace_period_hours: options.gracePeriodHours,
        notification_email: options.notificationEmail,
        telegram_chat_id: options.telegramChatId,
        vacation_mode: options.vacationMode,
        vacation_until: options.vacationUntil,
      }),
    });

    if (!response.ok) {
      throw new Error(`Configuration failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Start automatic heartbeat at specified interval.
   */
  startAutoHeartbeat(intervalMs: number = 3600000): void {
    if (this.heartbeatInterval) {
      return;
    }

    // Send initial heartbeat
    this.heartbeat().catch(console.error);

    // Schedule recurring heartbeats
    this.heartbeatInterval = setInterval(() => {
      this.heartbeat().catch(console.error);
    }, intervalMs);
  }

  /**
   * Stop automatic heartbeat.
   */
  stopAutoHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = undefined;
    }
  }

  /**
   * Get the registration ID.
   */
  getRegistrationId(): string | undefined {
    return this.registrationId;
  }
}

/**
 * Convenience function to register and return a configured client.
 */
export async function register(options: RegisterOptions): Promise<RedSwitch> {
  const client = new RedSwitch();
  await client.register(options);
  return client;
}

export default RedSwitch;
