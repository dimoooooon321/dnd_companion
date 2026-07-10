export type CharacterInventoryItem = {
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
};
