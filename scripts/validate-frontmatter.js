#!/usr/bin/env node

/**
 * Chapter Frontmatter Validation Script
 *
 * Validates that all MDX files in docs/ have proper frontmatter
 * according to the chapter schema defined in the spec.
 *
 * Usage: node scripts/validate-frontmatter.js
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Chapter schema (from specs/001-physical-ai-book/contracts/chapter-schema.json concept)
const chapterSchema = {
  required: ['id', 'title', 'sidebar_position', 'description'],
  optional: ['keywords', 'hide_table_of_contents', 'learning_objectives', 'estimated_time'],
  patterns: {
    id: /^[a-z0-9-]+$/,
    title: { minLength: 10, maxLength: 80 },
    sidebar_position: { min: 1, max: 20 },
    description: { minLength: 50, maxLength: 200 },
  }
};

function extractFrontmatter(content) {
  const frontmatterRegex = /^---\n([\s\S]*?)\n---/;
  const match = content.match(frontmatterRegex);

  if (!match) {
    return null;
  }

  const frontmatterText = match[1];
  const frontmatter = {};

  // Simple YAML parsing (handles basic key-value pairs and arrays)
  const lines = frontmatterText.split('\n');
  let currentKey = null;
  let inArray = false;

  lines.forEach(line => {
    const trimmed = line.trim();

    if (!trimmed) return;

    // Array item
    if (trimmed.startsWith('-') && inArray) {
      const value = trimmed.substring(1).trim();
      frontmatter[currentKey].push(value);
    }
    // Key-value pair
    else if (trimmed.includes(':')) {
      const [key, ...valueParts] = trimmed.split(':');
      const value = valueParts.join(':').trim();

      if (value === '') {
        // Empty value - might be an array
        currentKey = key.trim();
        frontmatter[currentKey] = [];
        inArray = true;
      } else if (value.startsWith('[') && value.endsWith(']')) {
        // Inline array
        frontmatter[key.trim()] = value.slice(1, -1).split(',').map(v => v.trim());
        inArray = false;
      } else {
        // Regular value
        frontmatter[key.trim()] = value;
        inArray = false;
      }
    }
  });

  return frontmatter;
}

function validateFrontmatter(filePath, frontmatter) {
  const errors = [];

  if (!frontmatter) {
    errors.push('No frontmatter found');
    return errors;
  }

  // Check required fields
  chapterSchema.required.forEach(field => {
    if (!(field in frontmatter)) {
      errors.push(`Missing required field: ${field}`);
    }
  });

  // Validate patterns
  if (frontmatter.id && !chapterSchema.patterns.id.test(frontmatter.id)) {
    errors.push(`Invalid id format: ${frontmatter.id} (must be lowercase alphanumeric with dashes)`);
  }

  if (frontmatter.title) {
    const titleLength = frontmatter.title.length;
    if (titleLength < chapterSchema.patterns.title.minLength) {
      errors.push(`Title too short: ${titleLength} chars (minimum ${chapterSchema.patterns.title.minLength})`);
    }
    if (titleLength > chapterSchema.patterns.title.maxLength) {
      errors.push(`Title too long: ${titleLength} chars (maximum ${chapterSchema.patterns.title.maxLength})`);
    }
  }

  if (frontmatter.sidebar_position) {
    const pos = parseInt(frontmatter.sidebar_position);
    if (pos < chapterSchema.patterns.sidebar_position.min || pos > chapterSchema.patterns.sidebar_position.max) {
      errors.push(`Invalid sidebar_position: ${pos} (must be between ${chapterSchema.patterns.sidebar_position.min}-${chapterSchema.patterns.sidebar_position.max})`);
    }
  }

  if (frontmatter.description) {
    const descLength = frontmatter.description.length;
    if (descLength < chapterSchema.patterns.description.minLength) {
      errors.push(`Description too short: ${descLength} chars (minimum ${chapterSchema.patterns.description.minLength})`);
    }
    if (descLength > chapterSchema.patterns.description.maxLength) {
      errors.push(`Description too long: ${descLength} chars (maximum ${chapterSchema.patterns.description.maxLength})`);
    }
  }

  return errors;
}

function main() {
  console.log('🔍 Validating chapter frontmatter...\n');

  const docsDir = path.join(process.cwd(), 'docs');

  if (!fs.existsSync(docsDir)) {
    console.log('ℹ️  No docs/ directory found yet - skipping validation');
    process.exit(0);
  }

  const mdxFiles = glob.sync('**/*.{md,mdx}', { cwd: docsDir });

  if (mdxFiles.length === 0) {
    console.log('ℹ️  No MDX files found in docs/ - skipping validation');
    process.exit(0);
  }

  let totalErrors = 0;
  let filesChecked = 0;

  mdxFiles.forEach(file => {
    const filePath = path.join(docsDir, file);
    const content = fs.readFileSync(filePath, 'utf-8');
    const frontmatter = extractFrontmatter(content);
    const errors = validateFrontmatter(filePath, frontmatter);

    filesChecked++;

    if (errors.length > 0) {
      console.log(`❌ ${file}:`);
      errors.forEach(error => console.log(`   - ${error}`));
      console.log('');
      totalErrors += errors.length;
    }
  });

  if (totalErrors === 0) {
    console.log(`✅ All ${filesChecked} file(s) have valid frontmatter`);
    process.exit(0);
  } else {
    console.log(`\n❌ Found ${totalErrors} error(s) in ${filesChecked} file(s)`);
    process.exit(1);
  }
}

main();
