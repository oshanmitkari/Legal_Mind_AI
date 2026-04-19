# 🎨 LegalMind AI - Visual Design Guide

## F6 (AI Assistant) + F11 (Precedent Finder) - Refactored UI

---

## 📐 **Layout Structure**

### **Main Container**
```
┌─────────────────────────────────────────────────────────────┐
│  CASE DETAIL PAGE                                           │
├─────────────────────────────────────────────────────────────┤
│  Case Summary Cards (4-column grid)                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────┬─────────────────────────┐  │
│  │ LEFT COLUMN (60%)           │ RIGHT COLUMN (40%)      │  │
│  │                             │                         │  │
│  │ ┌─────────────────────────┐ │ ┌─────────────────────┐ │  │
│  │ │ Documents Section       │ │ │ Deadlines           │ │  │
│  │ └─────────────────────────┘ │ └─────────────────────┘ │  │
│  │                             │                         │  │
│  │ ┌─────────────────────────┐ │ ┌─────────────────────┐ │  │
│  │ │ ╔═══════════════════╗   │ │ │ Drafting Tools      │ │  │
│  │ │ ║ TABBED INTERFACE  ║   │ │ └─────────────────────┘ │  │
│  │ │ ╠═══════════════════╣   │ │                         │  │
│  │ │ ║ [AI] [Precedent]  ║   │ │                         │  │
│  │ │ ╠═══════════════════╣   │ │                         │  │
│  │ │ ║                   ║   │ │                         │  │
│  │ │ ║  Active Tab       ║   │ │                         │  │
│  │ │ ║  Content          ║   │ │                         │  │
│  │ │ ║                   ║   │ │                         │  │
│  │ │ ╚═══════════════════╝   │ │                         │  │
│  │ └─────────────────────────┘ │                         │  │
│  └─────────────────────────────┴─────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 **Tab Navigation Design**

### **Tab Bar**
```
┌─────────────────────────────────────────────────────────────┐
│ ┌──────────────────┐ ┌──────────────────┐                   │
│ │ 💬 AI Assistant  │ │ 📄 Precedent     │                   │
│ │ ════════════════ │ │ Finder           │                   │
│ └──────────────────┘ └──────────────────┘                   │
│        ACTIVE            INACTIVE                            │
│   (cyan border)      (transparent)                           │
└─────────────────────────────────────────────────────────────┘
```

**Visual States**:
- **Active Tab**: Cyan bottom border (2px), cyan text (#06b6d4)
- **Inactive Tab**: Transparent border, slate-400 text
- **Hover**: slate-300 text color

---

## 🤖 **AI Assistant Tab (F6) - Component Breakdown**

### **1. Header Section**
```
┌─────────────────────────────────────────────────────────────┐
│ ┌──┐                                           ┌──────────┐ │
│ │🤖│ Legal AI Agent                            │ 5 msgs   │ │
│ └──┘ Context-aware case analysis with RAG      └──────────┘ │
│      (Gradient cyan avatar)                    (Badge)      │
└─────────────────────────────────────────────────────────────┘
```

### **2. Chat Container (500px height)**
```
┌─────────────────────────────────────────────────────────────┐
│                         CHAT MESSAGES                        │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│ ┌──┐                                                         │
│ │⚡│ AI Agent                                                │
│ └──┘                                                         │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ AI response appears here with dark background...        │ │
│ │                                                         │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ 📄 Sources (2): document1.pdf  evidence.pdf        │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                              │
│                                            ┌──┐              │
│                                       You  │👤│              │
│                                            └──┘              │
│                          ┌─────────────────────────────────┐ │
│                          │ User question in cyan bubble   │ │
│                          └─────────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Message Alignment**:
- AI Messages: Left-aligned (max-width 85%)
- User Messages: Right-aligned (max-width 75%)

**Color Coding**:
- AI Bubble: slate-800 bg, slate-700 border
- User Bubble: cyan-500 bg, slate-950 text
- Avatar: Gradient (cyan-500 → cyan-600)

### **3. Input Area**
```
┌─────────────────────────────────────────────────────────────┐
│ ┌───────────────────────────────────────────┐ ┌──────────┐ │
│ │ Ask about case strategy, documents... 🛫  │ │   Send → │ │
│ └───────────────────────────────────────────┘ └──────────┘ │
│  (slate-950 bg, slate-700 border)         (Gradient btn)   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 **Precedent Finder Tab (F11) - Component Breakdown**

### **1. Header with Search Button**
```
┌─────────────────────────────────────────────────────────────┐
│ ┌──┐                                  ┌───────────────────┐ │
│ │🔍│ Precedent Search Engine          │ 🔍 Find Similar  │ │
│ └──┘ FAISS vector similarity + AI     │    Cases         │ │
│                                       └───────────────────┘ │
│  (Gradient avatar)                    (Gradient button)    │
└─────────────────────────────────────────────────────────────┘
```

### **2. Statistics Banner**
```
┌─────────────────────────────────────────────────────────────┐
│ ┌─────────────┬──────────────┬──────────────┐               │
│ │      3      │    85.2%     │      50      │  Cyan gradient│
│ │  Matches    │  Avg Sim     │   Cases      │  background   │
│ │   Found     │  Score       │  Searched    │               │
│ └─────────────┴──────────────┴──────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

### **3. Precedent Card**
```
┌─────────────────────────────────────────────────────────────┐
│ ┌──┐ CRL/2020/001                           📊 85.7%        │
│ │1 │ State vs. Rajesh Kumar           Excellent Match       │
│ └──┘                                    (emerald badge)     │
│ ─────────────────────────────────────────────────────────── │
│ ┌───────────────────────────────────────────────────────┐   │
│ │ Type: Criminal       Court: Sessions Court, Delhi    │   │
│ │ Date: 2020-05-15     Sections: IPC 302, 34          │   │
│ └───────────────────────────────────────────────────────┘   │
│                                                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ▼ View Full Details                                     │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                              │
│ (Hover: cyan border + shadow)                               │
└─────────────────────────────────────────────────────────────┘
```

**Match Quality Badges**:
```
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ Excellent      │  │ Good Match     │  │ Moderate       │
│ Match          │  │                │  │ Match          │
│ (>= 80%)       │  │ (60-79%)       │  │ (< 60%)        │
│ emerald-300    │  │ cyan-300       │  │ amber-300      │
└────────────────┘  └────────────────┘  └────────────────┘
```

### **4. AI Comparison Report**
```
┌─────────────────────────────────────────────────────────────┐
│ ┌──┐ AI Comparative Analysis      Powered by Gemini ───────┤
│ │⚡│                                                          │
│ └──┘ ──────────────────────────────────────────────────────│
│                                                              │
│ ## Similarity Analysis                                       │
│ These precedents were matched because they share...          │
│                                                              │
│ ## Legal Overlaps                                            │
│ • IPC Section 302 (Murder)                                   │
│ • IPC Section 34 (Common Intention)                          │
│                                                              │
│ ## Strategic Implications                                    │
│ Based on these precedents, consider...                       │
│                                                              │
│ (Markdown formatted, gradient background)                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 **Color System**

### **Primary Colors**
```
Cyan-500:  #06b6d4  ████  Buttons, highlights, active state
Cyan-400:  #22d3ee  ████  Text accents, labels
Cyan-300:  #67e8f9  ████  Badges, subtle highlights
```

### **Background Colors**
```
Slate-950: #020617  ████  Darkest backgrounds
Slate-900: #0f172a  ████  Card backgrounds
Slate-800: #1e293b  ████  Message bubbles
Slate-700: #334155  ████  Borders
```

### **Text Colors**
```
White:     #ffffff  ████  Primary text
Slate-300: #cbd5e1  ████  Body text
Slate-400: #94a3b8  ████  Secondary text
Slate-500: #64748b  ████  Tertiary text
```

### **Semantic Colors**
```
Emerald-300: #6ee7b7  ████  Success, excellent match
Amber-300:   #fcd34d  ████  Warning, moderate match
Rose-300:    #fda4af  ████  Error, delete actions
```

---

## 📏 **Spacing Scale**

```
gap-1:  4px    ▫ Tight spacing
gap-2:  8px    ▫▫ Standard tight
gap-3:  12px   ▫▫▫ Default spacing
gap-4:  16px   ▫▫▫▫ Section spacing
gap-6:  24px   ▫▫▫▫▫▫ Large spacing
```

---

## 🔤 **Typography Scale**

```
text-xs:    12px  "Sources (2):"
text-sm:    14px  Message text
text-base:  16px  Card titles
text-lg:    18px  Section headings
text-xl:    20px  Primary headings
text-2xl:   24px  Page titles
```

---

## ✨ **Interactive States**

### **Buttons**
- **Default**: Gradient bg, shadow-lg
- **Hover**: Increased shadow (shadow-xl), slight scale
- **Active**: Slight depression effect
- **Disabled**: Opacity 50%, cursor not-allowed

### **Cards**
- **Default**: slate-700 border
- **Hover**: cyan-500/50 border, shadow with cyan tint
- **Focus**: Ring effect (ring-cyan-500)

### **Inputs**
- **Default**: slate-700 border, slate-950 bg
- **Focus**: cyan-500 border, ring-cyan-500/20
- **Error**: rose-500 border

---

## 🎬 **Animations**

### **Tab Transitions**
```css
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
Duration: 0.3s ease-in-out
```

### **Typing Indicator**
```css
animate-bounce with staggered delays:
  Dot 1: 0ms
  Dot 2: 150ms
  Dot 3: 300ms
```

### **Hover Effects**
```css
transition-all (0.2s default)
  - Border color
  - Shadow
  - Transform (scale)
```

---

## 📱 **Responsive Behavior**

### **Breakpoints**
- **sm**: 640px  (Tablets)
- **md**: 768px  (Small laptops)
- **lg**: 1024px (Desktop - main layout split)
- **xl**: 1280px (Large desktop)

### **Layout Adaptations**
- **< lg**: Single column, tabs stack vertically
- **>= lg**: Two-column layout (60/40 split)
- **Chat height**: Fixed 500px on all screens

---

**Design System**: ✅ COMPLETE  
**Accessibility**: ♿ WCAG 2.1 AA Ready  
**Browser Support**: Chrome, Firefox, Safari, Edge (latest 2 versions)
