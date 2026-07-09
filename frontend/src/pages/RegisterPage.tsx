import { useState, type FormEvent } from 'react';
import { Alert, Button, Paper, Stack, TextField, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { register as registerRequest } from '../api/auth';
import { getApiErrorMessage } from '../lib/apiError';
import { PageShell } from '../components/PageShell';

export function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSuccess(null);
    setError(null);
    setIsSubmitting(true);

    try {
      await registerRequest({
        email,
        password,
        role: 'player',
      });

      setPassword('');
      setSuccess(`Аккаунт для ${email} успешно создан. Теперь можно войти в систему.`);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Не удалось зарегистрироваться.'));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <PageShell title="Register">
      <Typography variant="body1" color="text.secondary">
        Create a placeholder account for the frontend scaffold.
      </Typography>
      <Paper sx={{ p: 3, mt: 2, maxWidth: 480 }}>
        <form onSubmit={handleSubmit}>
          <Stack spacing={2}>
            {success ? <Alert severity="success">{success}</Alert> : null}
            {error ? <Alert severity="error">{error}</Alert> : null}
            <TextField
              label="Email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              fullWidth
              autoComplete="email"
            />
            <TextField
              label="Password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              fullWidth
              autoComplete="new-password"
            />
            <Button type="submit" variant="contained" size="large" disabled={isSubmitting}>
              {isSubmitting ? 'Creating account...' : 'Register'}
            </Button>
            <Button component={RouterLink} to="/login" variant="text">
              Back to login
            </Button>
            {success ? (
              <Button component={RouterLink} to="/login" variant="outlined">
                Go to login
              </Button>
            ) : null}
          </Stack>
        </form>
      </Paper>
    </PageShell>
  );
}
