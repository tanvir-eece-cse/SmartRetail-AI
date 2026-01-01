import { describe, it, expect } from 'vitest'

describe('App', () => {
  it('should pass basic test', () => {
    expect(true).toBe(true)
  })

  it('should have correct app name', () => {
    const appName = 'SmartRetail-AI'
    expect(appName).toContain('SmartRetail')
  })
})
