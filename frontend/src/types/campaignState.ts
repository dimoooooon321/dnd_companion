import type { Campaign } from './campaign';

export type CampaignCharacterState = {
  id: number;
  name: string;
  race: string;
  class_name: string;
  level: number;
  experience: number;
  max_hp: number;
  current_hp: number;
  strength?: number;
  dexterity?: number;
  constitution?: number;
  intelligence?: number;
  wisdom?: number;
  charisma?: number;
};

export type CampaignMonsterState = {
  id: number;
  campaign_id: number;
  monster_id: number;
  quantity: number;
  created_at: string;
  monster: {
    id: number;
    created_by: number;
    name: string;
    description: string;
    hp: number;
    armor_class: number;
    challenge_rating: number;
    image_url: string | null;
    created_at: string;
  };
};

export type CampaignEventState = {
  id: number;
  campaign_id: number;
  type: string;
  data: Record<string, unknown>;
  created_at: string;
};

export type CampaignSceneState = {
  id: number;
  campaign_id: number;
  title: string;
  description: string;
  image_url: string | null;
  is_active: boolean;
  created_at: string;
};

export type CampaignBattleTokenState = {
  id: number;
  x: number;
  y: number;
  character_id: number | null;
  monster_id: number | null;
};

export type CampaignBattleMapState = {
  id: number;
  width: number;
  height: number;
  tokens: CampaignBattleTokenState[];
};

export type CampaignState = {
  campaign: Campaign;
  current_scene: CampaignSceneState | null;
  characters: CampaignCharacterState[];
  monsters: CampaignMonsterState[];
  recent_events: CampaignEventState[];
  battle_maps: CampaignBattleMapState[];
};

export type CampaignBattleMapDetails = {
  id: number;
  campaign_id: number;
  name: string;
  width: number;
  height: number;
  created_at: string;
  tokens: Array<{
    id: number;
    battle_map_id: number;
    token_type: string;
    character_id: number | null;
    monster_id: number | null;
    x: number;
    y: number;
  }>;
};
