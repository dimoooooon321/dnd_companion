import api from './axios';
import type { Campaign } from '../types/campaign';
import type { CampaignBattleMapDetails, CampaignSceneState, CampaignState } from '../types/campaignState';
import type { CampaignCharacterState } from '../types/campaignState';
import type { MonsterSummary } from '../types/monster';

export type CreateCampaignPayload = {
  name: string;
  description: string;
};

export type CreateCampaignMonsterPayload = {
  monster_id: number;
  quantity: number;
};

export type CreateCampaignScenePayload = {
  title: string;
  description: string;
  image_url: string | null;
};

export type UpdateCharacterHpPayload = {
  hp: number;
};

export type MoveBattleTokenPayload = {
  x: number;
  y: number;
};

export async function getCampaigns() {
  return api.get<Campaign[]>('/campaigns');
}

export async function createCampaign(payload: CreateCampaignPayload) {
  return api.post<Campaign>('/campaigns', payload);
}

export async function getCampaign(campaignId: number) {
  return api.get<Campaign>(`/campaigns/${campaignId}`);
}

export async function getCampaignState(campaignId: number) {
  return api.get<CampaignState>(`/campaigns/${campaignId}/state`);
}

export async function getCampaignMonsters(campaignId: number) {
  return api.get<CampaignState['monsters']>(`/campaigns/${campaignId}/monsters`);
}

export async function getCampaignBattleMaps(campaignId: number) {
  return api.get<CampaignBattleMapDetails[]>(`/campaigns/${campaignId}/battle-maps`);
}

export async function getCampaignScenes(campaignId: number) {
  return api.get<CampaignSceneState[]>(`/campaigns/${campaignId}/scenes`);
}

export async function getMonsters() {
  return api.get<MonsterSummary[]>('/monsters');
}

export async function getCharacterInventory(characterId: number) {
  return api.get<{
    id: number;
    character_id: number;
    item_id: number;
    quantity: number;
    item: {
      id: number;
      name: string;
      description: string;
      item_type: string;
      weight: number;
      image_url: string | null;
      creator_id: number;
      created_at: string;
    };
  }[]>(`/characters/${characterId}/inventory`);
}

export async function addCampaignMonster(campaignId: number, payload: CreateCampaignMonsterPayload) {
  return api.post(`/campaigns/${campaignId}/monsters`, payload);
}

export async function createCampaignScene(campaignId: number, payload: CreateCampaignScenePayload) {
  return api.post(`/campaigns/${campaignId}/scenes`, payload);
}

export async function activateCampaignScene(campaignId: number, sceneId: number) {
  return api.patch(`/campaigns/${campaignId}/scenes/${sceneId}/activate`);
}

export async function updateCampaignCharacterHp(
  campaignId: number,
  characterId: number,
  payload: UpdateCharacterHpPayload
) {
  return api.patch<CampaignCharacterState>(`/campaigns/${campaignId}/characters/${characterId}/hp`, payload);
}

export async function moveBattleToken(tokenId: number, payload: MoveBattleTokenPayload) {
  return api.patch(`/battle-tokens/${tokenId}`, payload);
}
