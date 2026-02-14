/**
 * Tests for ClawHub Publisher
 */

const { ClawHubPublisher } = require('../lib/clawhub-publisher');
const fs = require('fs');
const path = require('path');

describe('ClawHubPublisher', () => {
  const mockToken = 'clh_test_token_12345';
  
  describe('constructor', () => {
    test('should use provided token', () => {
      const publisher = new ClawHubPublisher({ token: mockToken });
      expect(publisher.token).toBe(mockToken);
    });

    test('should use env token if not provided', () => {
      process.env.CLAWHUB_TOKEN = mockToken;
      const publisher = new ClawHubPublisher();
      expect(publisher.token).toBe(mockToken);
      delete process.env.CLAWHUB_TOKEN;
    });

    test('should use default registry', () => {
      const publisher = new ClawHubPublisher();
      expect(publisher.registry).toBe('https://www.clawhub.ai');
    });
  });

  describe('verifyToken', () => {
    test('should return invalid for empty token', async () => {
      const publisher = new ClawHubPublisher({ token: '' });
      const result = await publisher.verifyToken();
      expect(result.valid).toBe(false);
    });
  });

  describe('publish validation', () => {
    test('should throw error for missing slug', async () => {
      const publisher = new ClawHubPublisher({ token: mockToken });
      await expect(publisher.publish('./test', { name: 'Test' }))
        .rejects.toThrow('slug and name are required');
    });

    test('should throw error for missing name', async () => {
      const publisher = new ClawHubPublisher({ token: mockToken });
      await expect(publisher.publish('./test', { slug: 'test' }))
        .rejects.toThrow('slug and name are required');
    });

    test('should throw error for missing SKILL.md', async () => {
      const publisher = new ClawHubPublisher({ token: mockToken });
      await expect(publisher.publish('/nonexistent', { 
        slug: 'test', 
        name: 'Test' 
      })).rejects.toThrow('SKILL.md not found');
    });
  });

  describe('publishAll', () => {
    test('should return results for all skills', async () => {
      // Create mock skill directory
      const mockDir = '/tmp/test-skills';
      fs.mkdirSync(mockDir, { recursive: true });
      fs.mkdirSync(path.join(mockDir, 'skill1'), { recursive: true });
      fs.writeFileSync(path.join(mockDir, 'skill1', 'SKILL.md'), '# Test');

      const publisher = new ClawHubPublisher({ token: mockToken });
      
      // Mock publish to avoid actual API call
      publisher.publish = jest.fn().mockResolvedValue({ success: true });

      const results = await publisher.publishAll(mockDir, { version: '1.0.0' });
      
      expect(results).toHaveLength(1);
      expect(results[0].skill).toBe('skill1');

      // Cleanup
      fs.rmSync(mockDir, { recursive: true, force: true });
    });
  });
});
