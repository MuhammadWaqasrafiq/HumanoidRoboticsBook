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

  url: 'https://MuhammadWaqasrafiq.github.io',
  baseUrl: '/HumanoidRoboticsBook/',

  // GitHub pages deployment config.
  organizationName: 'MuhammadWaqasrafiq',
  projectName: 'HumanoidRoboticsBook',

  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',

  // FontAwesome Icons ke liye stylesheet integrate ki hai
  stylesheets: [
    {
      href: 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css',
      type: 'text/css',
    },
  ],

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  markdown: {
    mermaid: true,
  },

  themes: ['@docusaurus/theme-mermaid'],

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/MuhammadWaqasrafiq/HumanoidRoboticsBook/tree/main/',
          routeBasePath: '/',
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
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
              { label: 'Introduction', to: '/intro' },
              { label: 'Why Physical AI', to: '/why-physical-ai' },
            ],
          },
          {
            title: 'Resources',
            items: [
              { label: 'GitHub Repo', href: 'https://github.com/MuhammadWaqasrafiq/HumanoidRoboticsBook' },
              { label: 'Code Samples', href: 'https://github.com/MuhammadWaqasrafiq/HumanoidRoboticsBook/tree/main/code-examples' },
            ],
          },
          {
            title: 'Connect',
            items: [
              {
                html: `
                <div style="display: flex; flex-direction: column; gap: 8px; margin-top: -10px;">
                  <!-- Icons Row -->
                  <div style="display: flex; gap: 1.2rem; align-items: center;">
                    <a href="https://github.com/MuhammadWaqasrafiq/HumanoidRoboticsBook" target="_blank" rel="noopener noreferrer" style="color: #fff; font-size: 1.4rem;"><i class="fa-brands fa-github"></i></a>
                    <a href="https://linkedin.com/in/muhammadwaqasrafiq" target="_blank" rel="noopener noreferrer" style="color: #fff; font-size: 1.4rem;"><i class="fa-brands fa-linkedin"></i></a>
                    <a href="https://wa.me/923463033195" target="_blank" rel="noopener noreferrer" style="color: #fff; font-size: 1.4rem;"><i class="fa-brands fa-whatsapp"></i></a>
                    <a href="https://youtube.com/@your_channel" target="_blank" rel="noopener noreferrer" style="color: #fff; font-size: 1.4rem;"><i class="fa-brands fa-youtube"></i></a>
                  </div>
                  <!-- Compact License Link -->
                  <a href="https://github.com/MuhammadWaqasrafiq/HumanoidRoboticsBook/blob/main/LICENSE" target="_blank" rel="noopener noreferrer" style="font-size: 0.85rem; color: #3578e5; text-decoration: none; margin-top: 2px;">
                    MIT License <i class="fas fa-external-link-alt" style="font-size: 0.7rem;"></i>
                  </a>
                </div>
                `,
              },
            ],
          },
        ],
        // Professional Short Copyright
        copyright: `© ${new Date().getFullYear()} Embodied AI • MuhammadWaqasrafiq • MIT & CC-BY-4.0`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
        additionalLanguages: ['bash', 'python', 'cpp', 'yaml', 'json'],
      },
      algolia: {
        appId: 'YOUR_APP_ID',
        apiKey: 'YOUR_SEARCH_API_KEY',
        indexName: 'physical-ai-book',
        contextualSearch: true,
      },
      mermaid: {
        theme: { light: 'neutral', dark: 'dark' },
      },
    }),
};

module.exports = config;