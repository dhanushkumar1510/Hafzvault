import { normalizeEmail, validateEmail, validateUsername } from '../utils/validation.js';

describe('validateUsername', () => {
  it('accepts valid usernames', () => {
    ['abc', 'hafiz_01', 'a.b-c', 'x'.repeat(30)].forEach((u) => expect(validateUsername(u)).toBeNull());
  });
  it('rejects empty, short, long and illegal characters', () => {
    expect(validateUsername('')).toMatch(/Enter a username/);
    expect(validateUsername('ab')).toMatch(/3-30/);
    expect(validateUsername('x'.repeat(31))).toMatch(/3-30/);
    expect(validateUsername('has space')).toMatch(/3-30/);
    expect(validateUsername('emoji😀name')).toMatch(/3-30/);
  });
  it('trims surrounding spaces', () => {
    expect(validateUsername('  alice  ')).toBeNull();
  });
});

describe('validateEmail', () => {
  it('accepts valid emails', () => {
    expect(validateEmail('Alice@Example.com')).toBeNull();
    expect(validateEmail('a.b+c@sub.example.org')).toBeNull();
  });
  it('rejects invalid emails', () => {
    ['', 'nope', 'a@b', 'a b@c.com', '@c.com'].forEach((e) => expect(validateEmail(e)).toBeTruthy());
  });
  it('normalises to lowercase and trims', () => {
    expect(normalizeEmail('  Alice@Example.COM ')).toBe('alice@example.com');
  });
});
