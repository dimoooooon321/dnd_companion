import { useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import {
  activateCampaignScene,
  addCampaignMonster,
  createCampaignScene,
  moveBattleToken,
  updateCampaignCharacterHp,
} from '../../api/campaigns';
import { getApiErrorMessage } from '../../lib/apiError';
import type { CampaignBattleMapDetails, CampaignBattleMapState, CampaignSceneState, CampaignCharacterState } from '../../types/campaignState';
import type { MonsterSummary } from '../../types/monster';

type DialogKind = 'monster' | 'scene' | 'activate' | 'hp' | 'token' | null;

type DmControlsProps = {
  campaignId: number;
  characters: CampaignCharacterState[]; 
  scenes: CampaignSceneState[];
  availableMonsters: MonsterSummary[];
  battleMaps: CampaignBattleMapState[];
  battleMapDetailsById: Map<number, CampaignBattleMapDetails>;
};

const initialMonsterForm = {
  monsterId: '',
  quantity: '1',
};

const initialSceneForm = {
  title: '',
  description: '',
  imageUrl: '',
};

const initialHpForm = {
  characterId: '',
  hp: '',
};

const initialTokenForm = {
  battleMapId: '',
  tokenId: '',
  x: '0',
  y: '0',
};

export function DmControls({
  campaignId,
  characters,
  scenes,
  availableMonsters,
  battleMaps,
  battleMapDetailsById,
}: DmControlsProps) {
  const [activeDialog, setActiveDialog] = useState<DialogKind>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [monsterForm, setMonsterForm] = useState(initialMonsterForm);
  const [sceneForm, setSceneForm] = useState(initialSceneForm);
  const [activateSceneId, setActivateSceneId] = useState('');
  const [hpForm, setHpForm] = useState(initialHpForm);
  const [tokenForm, setTokenForm] = useState(initialTokenForm);

  useEffect(() => {
    if (activeDialog !== 'monster' || monsterForm.monsterId || availableMonsters.length === 0) {
      return;
    }

    setMonsterForm({
      monsterId: String(availableMonsters[0].id),
      quantity: '1',
    });
  }, [activeDialog, availableMonsters, monsterForm.monsterId]);

  useEffect(() => {
    if (activeDialog !== 'activate' || activateSceneId || scenes.length === 0) {
      return;
    }

    setActivateSceneId(String(scenes[0].id));
  }, [activeDialog, activateSceneId, scenes]);

  useEffect(() => {
    if (activeDialog !== 'hp' || hpForm.characterId || characters.length === 0) {
      return;
    }

    const firstCharacter = characters[0];
    setHpForm({
      characterId: String(firstCharacter.id),
      hp: String(firstCharacter.current_hp),
    });
  }, [activeDialog, characters, hpForm.characterId]);

  useEffect(() => {
    if (activeDialog !== 'token' || tokenForm.battleMapId || battleMaps.length === 0) {
      return;
    }

    const firstMap = battleMaps[0];
    const firstToken = firstMap.tokens[0];

    setTokenForm({
      battleMapId: String(firstMap.id),
      tokenId: firstToken ? String(firstToken.id) : '',
      x: firstToken ? String(firstToken.x) : '0',
      y: firstToken ? String(firstToken.y) : '0',
    });
  }, [activeDialog, battleMaps, tokenForm.battleMapId]);

  useEffect(() => {
    if (activeDialog !== 'token' || tokenForm.battleMapId === '') {
      return;
    }

    const selectedMap = battleMaps.find((battleMap) => String(battleMap.id) === tokenForm.battleMapId);
    const firstToken = selectedMap?.tokens[0];
    const selectedTokenExists = selectedMap?.tokens.some((token) => String(token.id) === tokenForm.tokenId);

    if (!selectedMap || selectedMap.tokens.length === 0) {
      return;
    }

    if (!selectedTokenExists && firstToken) {
      setTokenForm((current) => ({
        ...current,
        tokenId: String(firstToken.id),
        x: String(firstToken.x),
        y: String(firstToken.y),
      }));
    }
  }, [activeDialog, battleMaps, tokenForm.battleMapId, tokenForm.tokenId]);

  const handleClose = () => {
    if (isSubmitting) {
      return;
    }

    setActiveDialog(null);
    setError(null);
  };

  const openDialog = (dialog: Exclude<DialogKind, null>) => {
    setError(null);

    if (dialog === 'monster') {
      setMonsterForm(initialMonsterForm);
    }

    if (dialog === 'scene') {
      setSceneForm(initialSceneForm);
    }

    if (dialog === 'activate') {
      setActivateSceneId(scenes[0] ? String(scenes[0].id) : '');
    }

    if (dialog === 'hp') {
      const firstCharacter = characters[0];
      setHpForm(
        firstCharacter
          ? {
              characterId: String(firstCharacter.id),
              hp: String(firstCharacter.current_hp),
            }
          : initialHpForm
      );
    }

    if (dialog === 'token') {
      const firstMap = battleMaps[0];
      const firstToken = firstMap?.tokens[0];
      setTokenForm(
        firstMap
          ? {
              battleMapId: String(firstMap.id),
              tokenId: firstToken ? String(firstToken.id) : '',
              x: firstToken ? String(firstToken.x) : '0',
              y: firstToken ? String(firstToken.y) : '0',
            }
          : initialTokenForm
      );
    }

    setActiveDialog(dialog);
  };

  const finishAction = () => {
    setIsSubmitting(false);
    setActiveDialog(null);
    setError(null);
  };

  const handleAddMonster = async () => {
    const monsterId = Number(monsterForm.monsterId);
    const quantity = Number(monsterForm.quantity);

    if (Number.isNaN(monsterId) || Number.isNaN(quantity)) {
      setError('Проверьте данные монстра.');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await addCampaignMonster(campaignId, {
        monster_id: monsterId,
        quantity,
      });
      finishAction();
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Не удалось добавить монстра.'));
      setIsSubmitting(false);
    }
  };

  const handleCreateScene = async () => {
    setIsSubmitting(true);
    setError(null);

    try {
      await createCampaignScene(campaignId, {
        title: sceneForm.title.trim(),
        description: sceneForm.description.trim(),
        image_url: sceneForm.imageUrl.trim() ? sceneForm.imageUrl.trim() : null,
      });
      finishAction();
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Не удалось создать сцену.'));
      setIsSubmitting(false);
    }
  };

  const handleActivateScene = async () => {
    const sceneId = Number(activateSceneId);

    if (Number.isNaN(sceneId)) {
      setError('Выберите сцену для активации.');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await activateCampaignScene(campaignId, sceneId);
      finishAction();
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Не удалось активировать сцену.'));
      setIsSubmitting(false);
    }
  };

  const handleUpdateHp = async () => {
    const characterId = Number(hpForm.characterId);
    const hp = Number(hpForm.hp);

    if (Number.isNaN(characterId) || Number.isNaN(hp)) {
      setError('Проверьте значение HP.');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await updateCampaignCharacterHp(campaignId, characterId, { hp });
      finishAction();
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Не удалось обновить HP.'));
      setIsSubmitting(false);
    }
  };

  const handleMoveToken = async () => {
    const tokenId = Number(tokenForm.tokenId);
    const x = Number(tokenForm.x);
    const y = Number(tokenForm.y);

    if (Number.isNaN(tokenId) || Number.isNaN(x) || Number.isNaN(y)) {
      setError('Проверьте координаты токена.');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await moveBattleToken(tokenId, { x, y });
      finishAction();
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Не удалось переместить токен.'));
      setIsSubmitting(false);
    }
  };

  const selectedTokenMap = battleMaps.find((battleMap) => String(battleMap.id) === tokenForm.battleMapId);
  const selectedToken = selectedTokenMap?.tokens.find((token) => String(token.id) === tokenForm.tokenId) ?? null;
  const tokenMoveDisabled = battleMaps.length === 0 || battleMaps.every((battleMap) => battleMap.tokens.length === 0);

  return (
    <Paper variant="outlined" sx={{ p: 2 }}>
      <Stack spacing={2}>
        <Box>
          <Typography variant="h6">DM Controls</Typography>
          <Typography variant="body2" color="text.secondary">
            Управление кампанией доступно только DM.
          </Typography>
        </Box>

        <Grid container spacing={1.5}>
          <Grid item>
            <Button variant="contained" onClick={() => openDialog('monster')} disabled={availableMonsters.length === 0}>
              Add Monster
            </Button>
          </Grid>
          <Grid item>
            <Button variant="contained" onClick={() => openDialog('scene')}>
              Create Scene
            </Button>
          </Grid>
          <Grid item>
            <Button variant="contained" onClick={() => openDialog('activate')} disabled={scenes.length === 0}>
              Activate Scene
            </Button>
          </Grid>
          <Grid item>
            <Button variant="contained" onClick={() => openDialog('hp')} disabled={characters.length === 0}>
              Change HP
            </Button>
          </Grid>
          <Grid item>
            <Button variant="contained" onClick={() => openDialog('token')} disabled={tokenMoveDisabled}>
              Move Token
            </Button>
          </Grid>
        </Grid>
      </Stack>

      <Dialog open={activeDialog === 'monster'} onClose={handleClose} fullWidth maxWidth="sm">
        <DialogTitle>Add Monster</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ pt: 1 }}>
            {error ? <Alert severity="error">{error}</Alert> : null}
            <FormControl fullWidth>
              <InputLabel id="monster-select-label">Monster</InputLabel>
              <Select
                labelId="monster-select-label"
                label="Monster"
                value={monsterForm.monsterId}
                onChange={(event) => setMonsterForm((current) => ({ ...current, monsterId: String(event.target.value) }))}
              >
                {availableMonsters.length ? (
                  availableMonsters.map((monster) => (
                    <MenuItem key={monster.id} value={String(monster.id)}>
                      {monster.name}
                    </MenuItem>
                  ))
                ) : (
                  <MenuItem value="" disabled>
                    Бестиарий пуст
                  </MenuItem>
                )}
              </Select>
            </FormControl>
            <TextField
              label="Quantity"
              type="number"
              value={monsterForm.quantity}
              onChange={(event) => setMonsterForm((current) => ({ ...current, quantity: event.target.value }))}
              fullWidth
              inputProps={{ min: 1 }}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button onClick={handleAddMonster} variant="contained" disabled={isSubmitting || availableMonsters.length === 0}>
            {isSubmitting ? 'Saving...' : 'Add'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={activeDialog === 'scene'} onClose={handleClose} fullWidth maxWidth="sm">
        <DialogTitle>Create Scene</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ pt: 1 }}>
            {error ? <Alert severity="error">{error}</Alert> : null}
            <TextField
              label="Title"
              value={sceneForm.title}
              onChange={(event) => setSceneForm((current) => ({ ...current, title: event.target.value }))}
              fullWidth
            />
            <TextField
              label="Description"
              value={sceneForm.description}
              onChange={(event) => setSceneForm((current) => ({ ...current, description: event.target.value }))}
              fullWidth
              multiline
              minRows={3}
            />
            <TextField
              label="Image URL"
              value={sceneForm.imageUrl}
              onChange={(event) => setSceneForm((current) => ({ ...current, imageUrl: event.target.value }))}
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button
            onClick={handleCreateScene}
            variant="contained"
            disabled={isSubmitting || sceneForm.title.trim().length === 0 || sceneForm.description.trim().length === 0}
          >
            {isSubmitting ? 'Saving...' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={activeDialog === 'activate'} onClose={handleClose} fullWidth maxWidth="sm">
        <DialogTitle>Activate Scene</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ pt: 1 }}>
            {error ? <Alert severity="error">{error}</Alert> : null}
            <FormControl fullWidth>
              <InputLabel id="activate-scene-label">Scene</InputLabel>
              <Select
                labelId="activate-scene-label"
                label="Scene"
                value={activateSceneId}
                onChange={(event) => setActivateSceneId(String(event.target.value))}
              >
                {scenes.map((scene) => (
                  <MenuItem key={scene.id} value={String(scene.id)}>
                    {scene.title}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button onClick={handleActivateScene} variant="contained" disabled={isSubmitting || scenes.length === 0}>
            {isSubmitting ? 'Saving...' : 'Activate'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={activeDialog === 'hp'} onClose={handleClose} fullWidth maxWidth="sm">
        <DialogTitle>Change HP</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ pt: 1 }}>
            {error ? <Alert severity="error">{error}</Alert> : null}
            <FormControl fullWidth>
              <InputLabel id="hp-character-label">Character</InputLabel>
              <Select
                labelId="hp-character-label"
                label="Character"
                value={hpForm.characterId}
                onChange={(event) => {
                  const selectedCharacter = characters.find(
                    (character) => String(character.id) === String(event.target.value)
                  );

                  setHpForm({
                    characterId: String(event.target.value),
                    hp: selectedCharacter ? String(selectedCharacter.current_hp) : '',
                  });
                }}
              >
                {characters.map((character) => (
                  <MenuItem key={character.id} value={String(character.id)}>
                    {character.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="HP"
              type="number"
              value={hpForm.hp}
              onChange={(event) => setHpForm((current) => ({ ...current, hp: event.target.value }))}
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button onClick={handleUpdateHp} variant="contained" disabled={isSubmitting || characters.length === 0}>
            {isSubmitting ? 'Saving...' : 'Update'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={activeDialog === 'token'} onClose={handleClose} fullWidth maxWidth="md">
        <DialogTitle>Move Token</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ pt: 1 }}>
            {error ? <Alert severity="error">{error}</Alert> : null}
            <FormControl fullWidth>
              <InputLabel id="token-map-label">Battle map</InputLabel>
              <Select
                labelId="token-map-label"
                label="Battle map"
                value={tokenForm.battleMapId}
                onChange={(event) => {
                  const selectedMapId = String(event.target.value);
                  const selectedMap = battleMaps.find((battleMap) => String(battleMap.id) === selectedMapId);
                  const firstToken = selectedMap?.tokens[0];

                  setTokenForm({
                    battleMapId: selectedMapId,
                    tokenId: firstToken ? String(firstToken.id) : '',
                    x: firstToken ? String(firstToken.x) : '0',
                    y: firstToken ? String(firstToken.y) : '0',
                  });
                }}
              >
                {battleMaps.map((battleMap) => (
                  <MenuItem key={battleMap.id} value={String(battleMap.id)}>
                    {battleMapDetailsById.get(battleMap.id)?.name ?? `Боевая карта #${battleMap.id}`}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel id="token-id-label">Token</InputLabel>
              <Select
                labelId="token-id-label"
                label="Token"
                value={tokenForm.tokenId}
                onChange={(event) => {
                  const selectedMap = selectedTokenMap;
                  const selectedToken = selectedMap?.tokens.find((token) => String(token.id) === String(event.target.value));

                  setTokenForm((current) => ({
                    ...current,
                    tokenId: String(event.target.value),
                    x: selectedToken ? String(selectedToken.x) : current.x,
                    y: selectedToken ? String(selectedToken.y) : current.y,
                  }));
                }}
                disabled={!selectedTokenMap || selectedTokenMap.tokens.length === 0}
              >
                {selectedTokenMap?.tokens.map((token) => (
                  <MenuItem key={token.id} value={String(token.id)}>
                    Token #{token.id}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                label="X"
                type="number"
                value={tokenForm.x}
                onChange={(event) => setTokenForm((current) => ({ ...current, x: event.target.value }))}
                fullWidth
              />
              <TextField
                label="Y"
                type="number"
                value={tokenForm.y}
                onChange={(event) => setTokenForm((current) => ({ ...current, y: event.target.value }))}
                fullWidth
              />
            </Stack>

            {selectedToken ? (
              <Typography variant="body2" color="text.secondary">
                Selected token: #{selectedToken.id} at ({selectedToken.x}, {selectedToken.y})
              </Typography>
            ) : null}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button onClick={handleMoveToken} variant="contained" disabled={isSubmitting || tokenMoveDisabled}>
            {isSubmitting ? 'Saving...' : 'Move'}
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
}
