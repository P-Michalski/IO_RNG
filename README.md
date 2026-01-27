# 🎲 IO_RNG – Random Number Generator Testing Platform

<p align="left">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License" />
  <img src="https://img.shields.io/badge/python-3.x-blue.svg" alt="Python" />
  <img src="https://img.shields.io/badge/django-5.2.8-green.svg" alt="Django" />
  <img src="https://img.shields.io/badge/react-18.x-61dafb.svg" alt="React" />
  <img src="https://img.shields.io/badge/typescript-5.x-blue.svg" alt="TypeScript" />
</p>

A comprehensive web application for **testing and comparing Pseudo-Random Number Generators (PRNGs)** using industry‑standard statistical test suites. Built with modern technologies and **Clean Architecture** principles.

---

## 🎯 Features

### Core Functionality

- **10 RNG algorithms**: LCG, Park–Miller, PCG32, SplitMix64, Xorshift/Xoshiro256, AWCG, Blum Blum Shub, ChaCha20, Python Random, System RNG
- **32 statistical tests**:
  - 15 × NIST SP 800‑22
  - 15 × Diehard
  - 2 × basic tests

- **Multi‑language support**: Python, Rust, and C# generators via a unified interface
- **Interactive dashboard** with real‑time charts and analytics
- **Batch testing** with configurable parameters
- **Custom bit testing** (no database persistence required)
- **PDF report generation** with detailed statistics and visualizations

### Advanced Features

- **Bit compression** – up to 94% space reduction using Base64 encoding
- **Parametric generators** – customizable LCG and AWCG parameters
- **Comprehensive wiki** – detailed documentation for algorithms and tests (Polish & English)
- **Theme customization** – light/dark mode with accent color selection
- **Results history** – track and compare results over time

---

## 🏗️ Architecture

### Backend (Django REST Framework)

- Clean Architecture
- Repository Pattern
- Adapter Pattern
- Dependency Injection

### Frontend (React + TypeScript)

- React 18
- TypeScript
- Vite
- shadcn/ui
- Tailwind CSS
- Recharts

---

## 🚀 Quick Start

### Prerequisites

- Python 3.x
- Node.js 16+
- npm or yarn

---

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate      # Linux/macOS
# or
venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

API available at: **[http://localhost:8000/api/](http://localhost:8000/api/)**

---

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Application available at: **[http://localhost:5173](http://localhost:5173)**

---

## 🎲 Supported Generators

| Generator      | Language  | Type   | Notes                    |
| -------------- | --------- | ------ | ------------------------ |
| ChaCha20       | Rust      | CSPRNG | Cryptographically secure |
| Python Random  | Python    | PRNG   | Standard library         |
| Xoshiro256     | C# (.NET) | PRNG   | Fast, high‑quality       |
| LCG            | Python    | PRNG   | Parametric               |
| PCG32          | Python    | PRNG   | Modern LCG variant       |
| SplitMix64     | Python    | PRNG   | Seed generator           |
| Park–Miller    | Python    | PRNG   | Minimal standard         |
| AWCG           | Python    | PRNG   | Parametric               |
| Blum Blum Shub | Python    | CSPRNG | Cryptographically secure |
| System RNG     | Python    | CSPRNG | OS‑level, fast           |

---

## 📖 Documentation

Full technical documentation (Polish) is available in:

- `frontend/src/assets/IO_RNG.pdf`
- or via the **About** page inside the application

---

## 👥 Team

- **Piotr Michalski** – Frontend Development, UI/UX
- **Dominik Bienia** – Backend Architecture, Statistical Tests
- **Mateusz Kania** – Generator Implementations, Testing

---

## 📄 License

This project is licensed under the **MIT License**.
