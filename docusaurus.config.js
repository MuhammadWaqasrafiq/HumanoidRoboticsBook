// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const { themes } = require('prism-react-renderer');
const lightCodeTheme = themes.github;
const darkCodeTheme = themes.dracula;

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Embodied AI: The Future of Robotics',
  tagline: 'Crafting the Future of Intelligent Machines',
  favicon: 'img/new_logo.svg',

  // ================================
  // GitHub Pages configuration
  // ================================
  url: 'https://muhammadwaqasrafiq.github.io',
  baseUrl: '/HumanoidRoboticsBook/',

  organizationName: 'MuhammadWaqasrafiq',
  projectName: 'HumanoidRoboticsBook',
  trailingSlash: false, // Ye line zaroor add karen

  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',

  // ================================
  // External stylesheets (FontAwesome)
  // ================================
  stylesheets: [
    {
      href: 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css',
      type: 'text/css',
    },
  ],

  // ================================
  // i18n
  // ================================
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  // ================================
  // Markdown & Mermaid
  // ================================
  markdown: {
    mermaid: true,
  },
  themes: ['@docusaurus/theme-mermaid'],

  // ================================
  // Presets
  // ================================
  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl:
            'https://github.com/MuhammadWaqasrafiq/HumanoidRoboticsBook/tree/main/',
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],

  // ================================
  // Theme Config
  // ================================
  themeConfig: {
    image: 'img/social-card.jpg',

    navbar: {
      title: 'Embodied AI',
      logo: {
        alt: 'Embodied AI Logo',
        src: 'img/new_logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Book',
        },
        {
          href: 'https://github.com/MuhammadWaqasrafiq/HumanoidRoboticsBook',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },

    footer: {
      style: 'dark',
      links: [
        {
          title: 'Learn',
          items: [
            { label: 'Introduction', to: '/docs/intro' },
            { label: 'Why Physical AI', to: '/docs/why-physical-ai' },
          ],
        },
        {
          title: 'Resources',
          items: [
            {
              label: 'GitHub Repo',
              href: 'https://github.com/MuhammadWaqasrafiq/HumanoidRoboticsBook',
            },
            {
              label: 'Code Samples',
              href: 'https://github.com/MuhammadWaqasrafiq/HumanoidRoboticsBook/tree/main/code-examples',
            },
          ],
        },
        {
          title: 'Connect',
          items: [
            {
              html: `
<div style="display:flex; gap:1.5rem; margin-bottom:1rem;">
  <a href="https://github.com/MuhammadWaqasrafiq/HumanoidRoboticsBook" target="_blank" rel="noopener noreferrer" aria-label="GitHub" style="color:#fff;font-size:1.6rem;">
    <i class="fa-brands fa-github"></i>
  </a>
  <a href="https://linkedin.com/in/MuhammadWaqasrafiq" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn" style="color:#fff;font-size:1.6rem;">
    <i class="fa-brands fa-linkedin"></i>
  </a>
  <a href="https://wa.me/923463033195" target="_blank" rel="noopener noreferrer" aria-label="WhatsApp" style="color:#fff;font-size:1.6rem;">
    <i class="fa-brands fa-whatsapp"></i>
  </a>
  <a href="https://www.youtube.com/watch?v=dZTfXiPSZyE" target="_blank" rel="noopener noreferrer" aria-label="YouTube" style="color:#fff;font-size:1.6rem;">
    <i class="fa-brands fa-youtube"></i>
  </a>
</div>
              `,
            },
            {
              label: 'MIT License',
              href: 'https://github.com/MuhammadWaqasrafiq/HumanoidRoboticsBook/blob/main/LICENSE',
            },
          ],
        },
      ],
      copyright: `© ${new Date().getFullYear()} Embodied AI • Muhammad Waqas Rafiq • MIT & CC-BY-4.0`,
    },

    prism: {
      theme: lightCodeTheme,
      darkTheme: darkCodeTheme,
      additionalLanguages: ['bash', 'python', 'cpp', 'yaml', 'json'],
    },

    mermaid: {
      theme: { light: 'neutral', dark: 'dark' },
    },
  },
};

module.exports = config;
