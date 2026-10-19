import { ApiError, toApiError } from '../services/apiError.js';

describe('toApiError', () => {
  it('maps a 409 mismatch with its code and message', () => {
    const e = toApiError({ response: { status: 409, data: { code: 'username_email_mismatch', detail: 'Does not match.' } } });
    expect(e).toBeInstanceOf(ApiError);
    expect(e.kind).toBe('http');
    expect(e.status).toBe(409);
    expect(e.code).toBe('username_email_mismatch');
    expect(e.message).toBe('Does not match.');
  });
  it('maps 404 account_not_found', () => {
    const e = toApiError({ response: { status: 404, data: { code: 'account_not_found', detail: 'None yet.' } } });
    expect(e.status).toBe(404);
    expect(e.code).toBe('account_not_found');
  });
  it('flattens DRF field errors and uses the first as the message', () => {
    const e = toApiError({ response: { status: 400, data: { username: ['Too short.'], email: ['Invalid.'] } } });
    expect(e.fieldErrors).toEqual({ username: 'Too short.', email: 'Invalid.' });
    expect(e.message).toBe('Too short.');
  });
  it('flattens nested field errors', () => {
    const e = toApiError({ response: { status: 400, data: { file: { file: ['Bad type.'] } } } });
    expect(e.fieldErrors).toEqual({ file: 'Bad type.' });
  });
  it('marks 401 as auth and 5xx as server', () => {
    expect(toApiError({ response: { status: 401, data: { detail: 'No.' } } }).kind).toBe('auth');
    const s = toApiError({ response: { status: 502, data: { detail: 'Storage down.' } } });
    expect(s.kind).toBe('server');
    expect(s.message).toBe('Storage down.');
  });
  it('handles non-JSON error bodies', () => {
    const e = toApiError({ response: { status: 503, data: '<html>bad gateway</html>' } });
    expect(e.kind).toBe('server');
    expect(e.message).toMatch(/Something went wrong/);
  });
  it('maps timeouts and network failures', () => {
    expect(toApiError({ code: 'ECONNABORTED' }).kind).toBe('timeout');
    expect(toApiError(new Error('Network Error')).kind).toBe('network');
  });
  it('returns existing ApiError unchanged', () => {
    const original = new ApiError({ kind: 'network', message: 'x' });
    expect(toApiError(original)).toBe(original);
  });
});
