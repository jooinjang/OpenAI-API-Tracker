# OpenAI Usage Tracker - React Edition

> **Modern React-based OpenAI API usage tracking and analysis tool with Apple Design System**

A complete migration from the original Streamlit application to a modern React-based web application, featuring comprehensive usage analytics, beautiful visualizations, and an Apple-inspired design system.

## ✨ Features

### 📊 **Comprehensive Analytics**
- **Total cost tracking** with currency formatting
- **API request monitoring** with detailed breakdowns  
- **Active user analysis** with user management
- **Model usage distribution** with performance metrics

### 👥 **Multi-View Interface**
- **Dashboard**: Overall usage overview and key metrics
- **Users**: Detailed per-user analysis and insights
- **Projects**: Project-based usage tracking and budgets
- **API Keys**: Key management and permissions
- **Budgets**: Cost control and alert management

### 📁 **Smart Data Management**
- **Drag-and-drop file upload** with validation
- **JSON data processing** from OpenAI exports
- **Real-time data validation** and error handling
- **Export capabilities** (JSON, CSV formats)

### 🎨 **Apple Design System**
- **Native Apple aesthetics** with system fonts
- **Responsive design** for all screen sizes
- **Dark/Light theme support** with system preference detection
- **Smooth animations** with Apple-style easing
- **Accessibility-first** components and interactions

### ⚡ **Modern Architecture**
- **React 18** with TypeScript for type safety
- **Zustand** for lightweight state management
- **Vite** for lightning-fast development and builds
- **Tailwind CSS** with custom Apple design tokens
- **Component-based architecture** with reusable UI elements

## 🚀 Quick Start

### Prerequisites
- **Node.js** (16.0 or higher)
- **npm** or **yarn** package manager

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd OpenAITracker/react-app

# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:3000`

### Building for Production

```bash
# Build optimized production bundle
npm run build

# Preview production build
npm run preview
```

## 📁 Project Structure

```
react-app/
├── public/                 # Static assets
├── src/
│   ├── components/         # React components
│   │   ├── ui/            # Reusable UI components
│   │   ├── layout/        # Layout components
│   │   └── views/         # Page components
│   ├── store/             # Zustand state management
│   ├── types/             # TypeScript type definitions
│   ├── utils/             # Utility functions
│   ├── App.tsx            # Main application component
│   ├── main.tsx           # Application entry point
│   └── index.css          # Global styles & Apple Design System
├── package.json           # Dependencies and scripts
├── tailwind.config.js     # Tailwind CSS configuration
├── tsconfig.json          # TypeScript configuration
└── vite.config.ts         # Vite build configuration
```

## 🔧 Key Components

### **Core UI Components**
- `AppleButton` - Apple-style buttons with variants
- `AppleCard` - Container cards with hover effects
- `MetricCard` - Dashboard metric display cards
- `FileUpload` - Drag-and-drop file upload interface

### **Layout Components**
- `MainLayout` - Application shell with sidebar
- `Sidebar` - Navigation and data status sidebar

### **View Components**
- `Dashboard` - Main analytics dashboard
- Additional views for Users, Projects, API Keys, Budgets

### **State Management**
- `useAppStore` - Main application state with Zustand
- Persistent storage for user preferences
- Real-time data processing and computed values

## 📊 Data Processing

The application processes OpenAI usage data in the 2025 bucket structure format, supporting both current and legacy formats:

### 2025 User Data Structure (Recommended)
```json
{
  "data": [{
    "start_time": 1704067200,
    "end_time": 1704153600,
    "results": [{
      "user_id": "user_123",
      "start_time": 1704067200,
      "line_item": "gpt-4",
      "usage": {
        "prompt_tokens": 100,
        "completion_tokens": 50,
        "total_tokens": 150
      },
      "cost": 0.003,
      "operation": "completion"
    }]
  }]
}
```

### 2025 Project Data Structure (Recommended)
```json
{
  "data": [{
    "start_time": 1704067200,
    "end_time": 1704153600,
    "results": [{
      "project_id": "proj_abc123",
      "start_time": 1704067200,
      "line_item": "gpt-3.5-turbo",
      "usage": {
        "prompt_tokens": 200,
        "completion_tokens": 100,
        "total_tokens": 300
      },
      "cost": 0.0006,
      "operation": "completion"
    }]
  }]
}
```

### Legacy Format Support
The application also supports legacy formats with `result` instead of `results` and `model` instead of `line_item` for backward compatibility.

## 🎨 Design System

### **Color Palette**
```css
/* Apple Blue */
--apple-blue: #007AFF;
--apple-blue-hover: #0056CC;

/* Supporting Colors */
--apple-green: #34C759;
--apple-orange: #FF9500;
--apple-red: #FF3B30;
--apple-purple: #AF52DE;
```

### **Typography**
- **Font Family**: SF Pro Text, -apple-system, BlinkMacSystemFont
- **Font Weights**: 400 (Regular), 500 (Medium), 600 (Semibold), 700 (Bold)
- **Responsive Typography**: Fluid sizing with clamp() functions

### **Spacing System**
- Based on 4px grid system
- Consistent spacing variables (4px, 8px, 12px, 16px, 20px, 24px, 32px, 48px, 64px, 96px, 128px)

### **Border Radius**
- `apple-lg`: 12px for cards and buttons
- `apple-xl`: 16px for major containers

## 🔄 Migration from Streamlit

This React application is a complete rewrite of the original Streamlit-based OpenAI Usage Tracker, offering:

### **Improvements Over Streamlit Version**
- ✅ **Better Performance**: Client-side rendering and optimized bundles
- ✅ **Enhanced UX**: Smooth animations, better responsiveness
- ✅ **Modern Architecture**: Component-based, type-safe development
- ✅ **Customization**: Full control over styling and interactions
- ✅ **Offline Capabilities**: Works without server dependency
- ✅ **Better Mobile Support**: Responsive design from the ground up

### **Feature Parity**
- ✅ **All Original Features**: Data upload, processing, visualization
- ✅ **Enhanced Analytics**: Better metrics calculation and display
- ✅ **Improved File Handling**: Better validation and error handling
- ✅ **Export Functions**: JSON and CSV export capabilities

## 🛠️ Development

### **Available Scripts**

```bash
# Development
npm run dev          # Start development server with HMR
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint

# Type Checking
npm run type-check   # Run TypeScript compiler checks
```

### **Code Quality**
- **TypeScript**: Full type safety with strict mode
- **ESLint**: Code linting with React and TypeScript rules
- **Prettier**: Code formatting (configured in VSCode)

### **Development Features**
- **Hot Module Replacement**: Instant updates during development
- **Source Maps**: Debug support in development and production builds
- **Tree Shaking**: Optimized production bundles
- **Code Splitting**: Automatic chunk splitting for better loading

## 🧪 Testing

### **Sample Data Generation**
The application includes a sample data generator for development and testing:

```typescript
// Generate sample user data
const userData = generateSampleData('user', 50);

// Generate sample project data  
const projectData = generateSampleData('project', 30);
```

Click the "🧪 샘플 데이터 로드" button in the dashboard to load test data.

## 🔐 Security

### **Data Privacy**
- **Client-side Processing**: All data processing happens in the browser
- **No Server Storage**: Data is not sent to external servers
- **Local Storage Only**: Settings and preferences stored locally

### **File Upload Security**
- **Format Validation**: Only JSON files accepted
- **Size Limits**: 10MB maximum file size
- **Structure Validation**: Validates OpenAI data format
- **Error Handling**: Graceful error handling for invalid files

## 🚀 Deployment

### **Build Output**
```bash
npm run build
```

Generates optimized production files in the `dist/` directory:
- Minified JavaScript bundles with tree shaking
- Optimized CSS with unused styles removed
- Source maps for debugging
- Asset optimization and compression

### **Deployment Options**
- **Static Hosting**: Vercel, Netlify, GitHub Pages
- **CDN Deployment**: AWS CloudFront, Azure CDN
- **Self-hosted**: Any static file server (nginx, Apache)

### **Environment Configuration**
No environment variables required - fully client-side application.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Issues**: Report bugs and request features via GitHub Issues
- **Documentation**: Additional documentation available in the `/docs` directory
- **Migration Guide**: See `MIGRATION.md` for Streamlit to React migration details

---

**Built with ❤️ using React, TypeScript, and Apple Design System**