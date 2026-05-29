import { describe, it, expect } from 'vitest'
import config from '../docs/.vitepress/config'

describe('smoke', () => {
  it('site config loads with bilingual title', () => {
    expect(config.title).toContain('测度论')
    expect(config.markdown?.math).toBe(true)
  })
})
