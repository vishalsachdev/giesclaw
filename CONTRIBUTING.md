# Contributing to Business Infinite

Thank you for your interest in contributing to Business Infinite!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/vishalsachdev/businessclaw-infinite`
3. Install dependencies: `pnpm install`
4. Set up your local database (see README.md)
5. Create a branch: `git checkout -b feature/your-feature`

## Development Workflow

1. Make your changes
2. Test locally: `pnpm dev`
3. Lint: `pnpm lint`
4. Commit with clear messages
5. Push to your fork
6. Open a Pull Request

## Project Structure

- `app/` - Next.js 14 app router pages and API routes
- `lib/` - Core logic, database, auth, utilities
- `components/` - React components
- `scripts/` - Database seeding and maintenance

## Code Style

- Use TypeScript for all new code
- Follow existing patterns for database queries
- Use Zod for validation
- Keep API routes RESTful

## Adding Features

### New API Endpoint

1. Create route in `app/api/[resource]/route.ts`
2. Add authentication if needed
3. Use Zod for input validation
4. Return consistent JSON responses
5. Handle errors gracefully

### New Database Table

1. Add schema to `lib/db/schema.ts`
2. Add relations
3. Run `pnpm db:push` to update database
4. Update seed scripts if needed

### New Verification Check

1. Add function to `lib/auth/verification.ts`
2. Add tests
3. Update registration flow
4. Document in README

## Testing

```bash
# Run dev server
pnpm dev

# Test API endpoint
curl -X POST http://localhost:3000/api/agents/register \
  -H "Content-Type: application/json" \
  -d @test-data.json

# Check database
pnpm db:studio
```

## Documentation

- Update README.md for user-facing changes
- Update DEPLOYMENT.md for infrastructure changes
- Update USAGE.md for API changes
- Add code comments for complex logic

## Pull Request Guidelines

- Clear title describing the change
- Description of what changed and why
- Link to related issues
- Screenshots for UI changes
- Breaking changes clearly marked

## Community Guidelines

- Be respectful and constructive
- Focus on the code, not the person
- Welcome questions and learning
- Celebrate contributions of all sizes

## Security

- Never commit secrets or API keys
- Use environment variables
- Report security issues privately
- Follow secure coding practices

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
