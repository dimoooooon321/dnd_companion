export type MonsterSummary = {
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
