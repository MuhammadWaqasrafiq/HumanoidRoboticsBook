import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import styles from './index.module.css';
import { useInView } from 'react-intersection-observer';
import useBaseUrl from '@docusaurus/useBaseUrl';

// 1. Animation Component
function AnimatedSection({ children, className, style }) {
  const { ref, inView } = useInView({
    triggerOnce: true,
    threshold: 0.1,
  });

  return (
    <div
      ref={ref}
      style={style}
      className={clsx('animated-section', className, { 'is-visible': inView })}
    >
      {children}
    </div>
  );
}

// 2. Hero Section
function HomepageHero() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <h1 className="hero__title">Embodied AI: Mastering Physical AI</h1>
        <p className="hero__subtitle">From Theory to Reality: Build, Train, and Deploy Intelligent Robots.</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            Start Learning - 5min ⏱️
          </Link>
        </div>
      </div>
    </header>
  );
}

// 3. Feature Icons Data
const FeatureList = [
  {
    title: 'Comprehensive Curriculum',
    imgPath: 'https://cdn-icons-png.flaticon.com/512/3306/3306604.png',
    description: (
      <>From ROS2 fundamentals to advanced concepts like Visual Language Models (VLMs), our curriculum covers everything you need.</>
    ),
  },
  {
    title: 'Hands-on Projects',
    imgPath: 'https://cdn-icons-png.flaticon.com/512/1063/1063196.png',
    description: (
      <>Apply your knowledge with real-world projects, including building a butler robot and dexterous manipulation tasks.</>
    ),
  },
  {
    title: 'Simulation & Real-World',
    imgPath: 'https://cdn-icons-png.flaticon.com/512/2103/2103633.png',
    description: (
      <>Learn to bridge the gap between simulation (Isaac Sim) and reality with practical sim-to-real workflows.</>
    ),
  },
];

// 4. Feature Individual Component
function Feature({ imgPath, title, description, className }) {
  return (
    <div className={clsx('col col--4', className)}>
      <div className={clsx(styles.featureCard, 'padding--lg')}>
        <div className="text--center">
          <img src={imgPath} alt={title} style={{ width: '80px', height: '80px', marginBottom: '20px' }} />
        </div>
        <div className="text--center padding-horiz--md">
          <h3 style={{ fontWeight: 'bold' }}>{title}</h3>
          <p>{description}</p>
        </div>
      </div>
    </div>
  );
}

// 5. Main Features Section
function HomepageFeatures() {
  return (
    <AnimatedSection className={styles.features} style={{ padding: '4rem 0' }}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} className={`animated-item-${idx + 1}`} />
          ))}
        </div>
      </div>
    </AnimatedSection>
  );
}

// 6. What You'll Learn (FIXED TEXT COLOR)
function WhatYoullLearn() {
  const [hoveredIdx, setHoveredIdx] = React.useState(null);

  const cardStyle = (isHovered) => ({
    height: '100%',
    borderRadius: '16px',
    background: 'white',
    transition: 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
    boxShadow: isHovered
      ? '0 20px 40px rgba(53,120,229,0.25)'
      : '0 10px 30px rgba(0,0,0,0.08)',
    transform: isHovered ? 'translateY(-12px) scale(1.02)' : 'translateY(0)',
    border: `1px solid ${isHovered ? '#3578e5' : 'rgba(0,0,0,0.05)'}`,
  });

  const listItemStyle = {
    color: '#222',
    display: 'flex',
    alignItems: 'center', // Tick aur text ko line mein karne ke liye
    gap: '12px',
    marginBottom: '16px',
    fontSize: '1rem',
  };

  return (
    <AnimatedSection
      className={styles.whatYoullLearn}
      style={{
        background: 'linear-gradient(180deg, #0f2a44 0%, #1b3a61 100%)',
        padding: '4rem 0',
      }}
    >
      <div className="container">
        <h2 className="text--center" style={{ color: 'white', marginBottom: '3rem', fontSize: '2.5rem', fontWeight: 'bold' }}>
          What You'll Learn
        </h2>

        <div className="row" style={{ rowGap: '2rem' }}> {/* Mobile spacing */}
          {[
            ["ROS 2 Navigation & Perception", "NVIDIA Isaac Sim Simulation", "URDF Modeling & Digital Twins"],
            ["Vision-Language-Action Models", "Dexterous Manipulation", "Sim-to-Real Transfer"],
            ["Voice-to-Action Pipelines", "Building Embodied Agents", "Ethical AI in Robotics"],
          ].map((items, idx) => (
            <div key={idx} className="col col--4 margin-bottom--lg">
              <div
                className="card padding--lg"
                style={cardStyle(hoveredIdx === idx)}
                onMouseEnter={() => setHoveredIdx(idx)}
                onMouseLeave={() => setHoveredIdx(null)}
              >
                <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                  {items.map((text, i) => (
                    <li key={i} style={listItemStyle}>

                      <span style={{ fontWeight: '500' }}>{text}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </div>
    </AnimatedSection>
  );
}



// 7. Who Is This For Section
function WhoIsThisFor() {
  const [hoveredIdx, setHoveredIdx] = React.useState(null);

  const audienceData = [
    {
      title: "Robotics Enthusiasts",
      desc: "Makers and hobbyists looking to build practical skills and bring DIY projects to life with ROS 2.",
      icon: "🛠️",
      accent: "#b9b246ff" // yellow
    },
    {
      title: "AI/ML Engineers",
      desc: "Software engineers and ML experts transitioning into embodied intelligence and autonomous systems.",
      icon: "🧠",
      accent: "#e74c3c" // Red
    },
    {
      title: "Researchers",
      desc: "Academics and students seeking cutting-edge resources for physical AI and Sim-to-Real experimentation.",
      icon: "🔬",

      accent: "#4e54c8" // Purple
    }
  ];

  // Card Styles
  const getCardStyle = (index) => ({
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: '24px',
    padding: '3rem 2rem',
    background: 'white',
    transition: 'all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
    boxShadow: hoveredIdx === index
      ? `0 30px 60px rgba(0,0,0,0.12)`
      : '0 10px 25px rgba(0,0,0,0.04)',
    transform: hoveredIdx === index ? 'translateY(-15px) scale(1.03)' : 'translateY(0)',
    borderBottom: `6px solid ${hoveredIdx === index ? audienceData[index].accent : '#eee'}`,
    cursor: 'default',
  });

  return (
    <AnimatedSection className={styles.whoIsThisFor} style={{ padding: '6rem 0', background: '#fafbfc' }}>
      <div className="container">
        <div className="text--center" style={{ marginBottom: '4rem' }}>
          <h2 style={{ fontSize: '3rem', fontWeight: '800', color: '#1b3a61' }}>Who Is This Book For?</h2>
          <div style={{ width: '80px', height: '4px', background: '#3578e5', margin: '1rem auto 2rem', borderRadius: '2px' }}></div>
          <p style={{ maxWidth: '750px', margin: '0 auto', fontSize: '1.25rem', color: '#555', lineHeight: '1.6' }}>
            This comprehensive guide is meticulously crafted for those ready to lead the next revolution in Physical AI.
          </p>
        </div>

        <div className="row" style={{ rowGap: '2.5rem' }}>
          {audienceData.map((item, idx) => (
            <div key={idx} className="col col--4">
              <div
                style={getCardStyle(idx)}
                onMouseEnter={() => setHoveredIdx(idx)}
                onMouseLeave={() => setHoveredIdx(null)}
              >
                <div style={{
                  fontSize: '3.5rem',
                  marginBottom: '1.5rem',
                  filter: hoveredIdx === idx ? 'grayscale(0%)' : 'grayscale(40%)',
                  transition: '0.3s'
                }}>
                  {item.icon}
                </div>
                <h3 style={{
                  fontSize: '1.6rem',
                  fontWeight: '700',
                  color: hoveredIdx === idx ? item.accent : '#222',
                  transition: '0.3s'
                }}>
                  {item.title}
                </h3>
                <p style={{
                  fontSize: '1.1rem',
                  color: '#666',
                  textAlign: 'center',
                  lineHeight: '1.5',
                  margin: 0
                }}>
                  {item.desc}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </AnimatedSection>
  );
}

// 8. Call to Action
function FinalCallToAction() {
  const [isHovered, setIsHovered] = React.useState(false);

  // Button Style
  const buttonStyle = {
    padding: '1.2rem 3rem',
    fontSize: '1.4rem',
    fontWeight: '700',
    borderRadius: '50px',
    textDecoration: 'none',
    transition: 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
    display: 'inline-flex',
    alignItems: 'center',
    gap: '12px',
    backgroundColor: isHovered ? '#ffffff' : '#3578e5',
    color: isHovered ? '#1b3a61' : '#ffffff',
    boxShadow: isHovered 
      ? '0 15px 35px rgba(255, 255, 255, 0.3)' 
      : '0 10px 25px rgba(53, 120, 229, 0.4)',
    transform: isHovered ? 'scale(1.1) translateY(-5px)' : 'scale(1)',
    border: 'none',
  };

  return (
    <AnimatedSection 
      style={{ 
        background: 'linear-gradient(135deg, #0f2a44 0%, #1b3a61 100%)', 
        padding: '8rem 0',
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      {/* Decorative Background Circles */}
      <div style={{
        position: 'absolute',
        top: '-10%',
        right: '-5%',
        width: '300px',
        height: '300px',
        background: 'rgba(53, 120, 229, 0.1)',
        borderRadius: '50%',
        filter: 'blur(60px)'
      }}></div>
      <div style={{
        position: 'absolute',
        bottom: '-10%',
        left: '-5%',
        width: '250px',
        height: '250px',
        background: 'rgba(53, 120, 229, 0.1)',
        borderRadius: '50%',
        filter: 'blur(50px)'
      }}></div>

      <div className="container text--center" style={{ position: 'relative', zIndex: 1 }}>
        <h2 style={{ 
          fontSize: '3.5rem', 
          fontWeight: '800', 
          color: 'white', 
          marginBottom: '1.5rem',
          letterSpacing: '-1px'
        }}>
          Ready to Build the Future?
        </h2>
        
        <p style={{ 
          fontSize: '1.4rem', 
          color: 'rgba(255, 255, 255, 0.8)', 
          maxWidth: '650px', 
          margin: '0 auto 3.5rem',
          lineHeight: '1.6'
        }}>
          Join our open-source community, access exclusive resources, and start your journey into the world of Physical AI today.
        </p>

        <div style={{ perspective: '1000px' }}>
          <Link 
            className="button"
            to="/docs/intro"
            style={buttonStyle}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
          >
            Explore Chapters <span>📖</span>
          </Link>
        </div>

        <div style={{ marginTop: '3rem', color: 'rgba(255,255,255,0.4)', fontSize: '0.9rem' }}>
          No registration required • Open Source • Beginner Friendly
        </div>
      </div>
    </AnimatedSection>
  );
}
// 9. Main Home Page
export default function Home() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout
      title={`Welcome to ${siteConfig.title}`}
      description="Mastering Physical AI with ROS 2 and NVIDIA Isaac Sim">
      <HomepageHero />
      <main>
        <HomepageFeatures />
        <WhatYoullLearn />
        <WhoIsThisFor />
        <FinalCallToAction />
      </main>
    </Layout>
  );
}