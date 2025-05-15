# Multi-Level Cache Simulator

## Project Description

- Implements a **Multi-Level Cache Simulator** modeling L1 and L2 caches with configurable:
  - Cache size
  - Block size
  - Associativity
  - Replacement policies (LRU and FIFO)
  
- Simulates memory access using various realistic workload patterns:
  - Sequential
  - Looping
  - Random

- Tracks cache performance metrics such as:
  - Hit rates at each cache level
  - Average Memory Access Time (AMAT)

- Investigates the impact of cache design parameters on reducing access times for:
  - Data
  - Instructions

- Runs comprehensive experiments across multiple cache configurations and policies to:
  - Compare performance benefits
  - Identify optimal cache settings

- Provides visualizations to analyze:
  - AMAT trends versus block size, workload types, and replacement policies

- Offers practical insights into cache memory design and its role in improving system efficiency

---
## Installation

1. **Clone the repository:**

   - Using command line:
    ```bash
    git clone https://github.com/AcePenaflorida/multi-level-cache-simulator.git
    ```

   - Using **GitHub Desktop**:
     1. Open GitHub Desktop.
     2. Click **File** > **Clone repository**.
     3. Select the **URL** tab.
     4. Paste the URL:  
        `https://github.com/AcePenaflorida/multi-level-cache-simulator.git`
     5. Choose your local path and click **Clone**.

   - Using **VS Code**:
     1. Open VS Code.
     2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac) to open the Command Palette.
     3. Type **Git: Clone** and select it.
     4. Paste the URL:  
        `https://github.com/AcePenaflorida/multi-level-cache-simulator.git`
     5. Choose your local folder and wait for the clone to finish.
     6. Open the cloned folder in VS Code.

2. Navigate into the project directory (if using terminal):
    ```bash
    cd Multi-Level-Cache-Simulator
    ```

3. Create and activate a virtual environment (terminal):
    ```bash
    python -m venv venv
    .\venv\Scripts\activate   # Windows
    # OR for Mac/Linux
    source venv/bin/activate
    ```

4. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
