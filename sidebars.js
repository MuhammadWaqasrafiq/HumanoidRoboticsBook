/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  // Main tutorial sidebar for the book
  tutorialSidebar: [
    {
      type: 'doc',
      id: 'intro',
      label: 'Introduction',
    },
    {
      type: 'category',
      label: 'Part I: Foundation',
      collapsed: false,
      items: [
        {
          type: 'doc',
          id: 'why-physical-ai/index',
          label: '01. Why Physical AI Is the Next Frontier',
        },
        {
          type: 'doc',
          id: 'hardware-2026/index',
          label: '02. The Hardware You Actually Need in 2026',
        },
      ],
    },
    {
      type: 'category',
      label: 'Part II: ROS 2 & Simulation',
      collapsed: false,
      items: [
        {
          type: 'category',
          label: '03. ROS 2 – The Robotic Nervous System',
          items: [
            {
              type: 'doc',
              id: 'ros2-fundamentals/index',
              label: 'Overview',
            },
            {
              type: 'doc',
              id: 'ros2-fundamentals/nodes-topics',
              label: 'Nodes & Topics',
            },
            {
              type: 'doc',
              id: 'ros2-fundamentals/services-actions',
              label: 'Services & Actions',
            },
            {
              type: 'doc',
              id: 'ros2-fundamentals/parameters-launch',
              label: 'Parameters & Launch Files',
            },
            {
              type: 'doc',
              id: 'ros2-fundamentals/debugging-tools',
              label: 'Debugging Tools',
            },
          ],
        },
        {
          type: 'doc',
          id: 'urdf-digital-twins/index',
          label: '04. URDF & Digital Twins',
        },
        {
          type: 'doc',
          id: 'simulation-ecosystem/index',
          label: '05. Gazebo vs Isaac Sim',
        },
        {
          type: 'doc',
          id: 'isaac-platform/index',
          label: '06. NVIDIA Isaac Platform',
        },
      ],
    },
    {
      type: 'category',
      label: 'Part III: Core Robotics',
      collapsed: false,
      items: [
        {
          type: 'doc',
          id: 'perception-stack/perception-stack',
          label: '07. Perception Stack',
        },
        {
          type: 'doc',
          id: 'bipedal-locomotion/index',
          label: '08. Bipedal Locomotion',
        },
        {
          type: 'doc',
          id: 'dexterous-manipulation/index',
          label: '09. Dexterous Manipulation',
        },
      ],
    },
    {
      type: 'category',
      label: 'Part IV: Intelligence Layer',
      collapsed: false,
      items: [
        {
          type: 'doc',
          id: 'vla-models/index',
          label: '10. Vision-Language-Action Models',
        },
        {
          type: 'doc',
          id: 'voice-to-action/index',
          label: '11. Voice-to-Action Pipeline',
        },
        {
          type: 'doc',
          id: 'sim-to-real/index',
          label: '12. Sim-to-Real Transfer',
        },
      ],
    },
    {
      type: 'category',
      label: 'Part V: Integration',
      collapsed: false,
      items: [
        {
          type: 'doc',
          id: 'capstone-butler/index',
          label: '13. Capstone: Autonomous Butler',
        },
      ],
    },
    {
      type: 'category',
      label: 'Appendices',
      collapsed: true,
      items: [
        {
          type: 'doc',
          id: 'appendices/lab-build-guides',
          label: 'A. Lab Build Guides',
        },
        {
          type: 'doc',
          id: 'appendices/troubleshooting-bible',
          label: 'B. Troubleshooting Bible',
        },
        {
          type: 'doc',
          id: 'appendices/future-roadmap',
          label: 'C. Future Roadmap (2026-2030)',
        },
      ],
    },
  ],
};

module.exports = sidebars;
