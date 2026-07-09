import api from './axios';
import type { Campaign } from '../types/campaign';
import type { CampaignBattleMapDetails, CampaignState } from '../types/campaignState';

export async function getCampaigns() {
  return api.get<Campaign[]>('/campaigns');
}

export async function getCampaign(campaignId: number) {
  return api.get<Campaign>(`/campaigns/${campaignId}`);
}

export async function getCampaignState(campaignId: number) {
  return api.get<CampaignState>(`/campaigns/${campaignId}/state`);
}

export async function getCampaignBattleMaps(campaignId: number) {
  return api.get<CampaignBattleMapDetails[]>(`/campaigns/${campaignId}/battle-maps`);
}
