export type Campaign = {
  id: number;
  name: string;
  description: string | null;
  dm_id: number;
  created_at: string;
  participant_count?: number;
  participants_count?: number;
  members_count?: number;
};
