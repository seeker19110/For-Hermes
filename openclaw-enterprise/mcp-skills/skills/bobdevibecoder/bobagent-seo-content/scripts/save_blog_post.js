#!/usr/bin/env node
/**
 * Save a blog post JSON to a product's content directory.
 * Usage: node save_blog_post.js <product_slug> <post_slug> '<post_json>'
 * Example: node save_blog_post.js micro-saas-template how-to-convert-json '{"title":"..."}'
 *
 * Also accepts a file path as the third argument.
 */

const fs = require("fs");
const path = require("path");

const productSlug = process.argv[2];
const postSlug = process.argv[3];
const postJsonOrPath = process.argv[4];

if (!productSlug || !postSlug || !postJsonOrPath) {
  console.error("Usage: node save_blog_post.js <product_slug> <post_slug> '<post_json>'");
  process.exit(1);
}

// Parse the post data
let postData;
try {
  postData = JSON.parse(postJsonOrPath);
} catch {
  // Try reading from file path
  try {
    postData = JSON.parse(fs.readFileSync(postJsonOrPath, "utf8"));
  } catch (e) {
    console.error("Failed to parse post JSON:", e.message);
    process.exit(1);
  }
}

// Validate required fields
const required = ["title", "description", "date", "tags", "sections"];
for (const field of required) {
  if (!postData[field]) {
    console.error(`Missing required field: ${field}`);
    process.exit(1);
  }
}

if (!Array.isArray(postData.sections) || postData.sections.length === 0) {
  console.error("Post must have at least one section");
  process.exit(1);
}

// Determine product directory
const productDir = path.join("/home/milad", productSlug);
if (!fs.existsSync(productDir)) {
  console.error(`Product directory not found: ${productDir}`);
  process.exit(1);
}

// Create blog content directory if needed
const blogDir = path.join(productDir, "src/content/blog");
fs.mkdirSync(blogDir, { recursive: true });

// Save the post
const filePath = path.join(blogDir, `${postSlug}.json`);
fs.writeFileSync(filePath, JSON.stringify(postData, null, 2) + "\n", "utf8");

// Count total posts
const totalPosts = fs.readdirSync(blogDir).filter((f) => f.endsWith(".json")).length;

console.log(JSON.stringify({
  status: "SAVE_SUCCESS",
  product: productSlug,
  post: postSlug,
  path: filePath,
  totalPosts,
  title: postData.title,
}));
