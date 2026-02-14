import type { ExecuteJobResult } from "../../runtime/offeringTypes.js";

/**
 * Content Creation Service Handler
 * Generates high-quality content for crypto and AI projects
 */

export async function executeJob(request: any): Promise<ExecuteJobResult> {
  const { topic, format, tone = "professional", length = "medium", target_audience = "crypto enthusiasts", key_points = [] } = request;

  // Generate content based on format
  let deliverable: string;

  switch (format) {
    case "twitter_thread":
      deliverable = generateTwitterThread(topic, tone, length, target_audience, key_points);
      break;
    case "blog_post":
      deliverable = generateBlogPost(topic, tone, length, target_audience, key_points);
      break;
    case "marketing_copy":
      deliverable = generateMarketingCopy(topic, tone, length, target_audience, key_points);
      break;
    case "newsletter":
      deliverable = generateNewsletter(topic, tone, length, target_audience, key_points);
      break;
    default:
      deliverable = generateTwitterThread(topic, tone, length, target_audience, key_points);
  }

  return { deliverable };
}

export function validateRequirements(request: any): boolean {
  // Validate required fields
  if (!request.topic || typeof request.topic !== "string") {
    return false;
  }
  if (!request.format || !["twitter_thread", "blog_post", "marketing_copy", "newsletter"].includes(request.format)) {
    return false;
  }
  // Validate optional fields if provided
  if (request.tone && !["professional", "casual", "hype", "educational", "witty"].includes(request.tone)) {
    return false;
  }
  if (request.length && !["short", "medium", "long"].includes(request.length)) {
    return false;
  }
  return true;
}

function generateTwitterThread(topic: string, tone: string, length: string, audience: string, keyPoints: string[]): string {
  const tweetCount = length === "short" ? 3 : length === "medium" ? 5 : 8;
  
  let content = `🧵 ${tweetCount}-Tweet Thread: ${topic}\n\n`;
  content += `1/ ${getHook(topic, tone)}\n\n`;
  
  for (let i = 2; i <= tweetCount; i++) {
    content += `${i}/ ${getTweetContent(topic, tone, i, tweetCount, keyPoints)}\n\n`;
  }
  
  content += `Like & RT if you found this helpful! 🔥`;
  return content;
}

function generateBlogPost(topic: string, tone: string, length: string, audience: string, keyPoints: string[]): string {
  const wordCount = length === "short" ? 300 : length === "medium" ? 800 : 1500;
  
  let content = `# ${topic}\n\n`;
  content += `## Introduction\n\n`;
  content += `${getIntro(topic, tone, audience)}\n\n`;
  
  if (keyPoints.length > 0) {
    content += `## Key Points\n\n`;
    keyPoints.forEach((point, index) => {
      content += `${index + 1}. ${point}\n\n`;
    });
  }
  
  content += `## Conclusion\n\n`;
  content += `${getConclusion(topic, tone)}\n\n`;
  
  return content;
}

function generateMarketingCopy(topic: string, tone: string, length: string, audience: string, keyPoints: string[]): string {
  let content = `🚀 ${topic}\n\n`;
  content += `${getHook(topic, tone)}\n\n`;
  content += `✨ What makes us different:\n`;
  
  if (keyPoints.length > 0) {
    keyPoints.forEach(point => {
      content += `• ${point}\n`;
    });
  } else {
    content += `• Cutting-edge technology\n`;
    content += `• Community-driven\n`;
    content += `• Built for ${audience}\n`;
  }
  
  content += `\n👉 Join the revolution today!`;
  return content;
}

function generateNewsletter(topic: string, tone: string, length: string, audience: string, keyPoints: string[]): string {
  let content = `📧 Weekly Update: ${topic}\n\n`;
  content += `Hey ${audience},\n\n`;
  content += `${getIntro(topic, tone, audience)}\n\n`;
  
  if (keyPoints.length > 0) {
    content += `📰 This Week's Highlights:\n\n`;
    keyPoints.forEach((point, index) => {
      content += `${index + 1}. ${point}\n\n`;
    });
  }
  
  content += `\nStay tuned for more updates!\n`;
  content += `— BobAgent`;
  
  return content;
}

function getHook(topic: string, tone: string): string {
  const hooks: Record<string, string[]> = {
    professional: [
      `A comprehensive analysis of ${topic} reveals key insights for strategic decision-making.`,
      `The landscape of ${topic} is evolving rapidly. Here's what you need to know.`,
    ],
    casual: [
      `Let me tell you something interesting about ${topic}...`,
      `Ever wondered about ${topic}? Here's the tea ☕`,
    ],
    hype: [
      `🚨 ${topic} is about to EXPLODE and here's why you can't miss it! 🚀`,
      `This changes EVERYTHING about ${topic} 🔥`,
    ],
    educational: [
      `Understanding ${topic}: A thread 🧵`,
      `Let's break down ${topic} step by step.`,
    ],
    witty: [
      `${topic}: Because apparently, we needed more chaos in our lives 😅`,
      `Plot twist: ${topic} is actually interesting. Here's why:`,
    ],
  };
  
  const toneHooks = hooks[tone] || hooks.professional;
  return toneHooks[Math.floor(Math.random() * toneHooks.length)];
}

function getTweetContent(topic: string, tone: string, index: number, total: number, keyPoints: string[]): string {
  if (keyPoints.length > 0 && index - 2 < keyPoints.length) {
    return keyPoints[index - 2];
  }
  return `More insights on ${topic} coming your way...`;
}

function getIntro(topic: string, tone: string, audience: string): string {
  return `Today we're diving deep into ${topic}. This is essential reading for ${audience} who want to stay ahead of the curve.`;
}

function getConclusion(topic: string, tone: string): string {
  return `In conclusion, ${topic} represents a significant opportunity for those paying attention. The future belongs to the informed.`;
}
