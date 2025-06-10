# Solar Equipment Explorer v2 - Architecture Migration Plan

## Migration Context & Intent

### Current State Problems
1. **Monolithic Structure**: All functionality is crammed into a single 880-line `solar_explorer.py` file
2. **Code Duplication**: Each equipment type has nearly identical display, filter, and visualization logic
3. **Tight Coupling**: Data loading, UI rendering, and business logic are intertwined
4. **Hard to Maintain**: Adding new equipment types requires copying large code blocks
5. **No Testing**: Current structure makes it difficult to write unit tests
6. **Configuration Issues**: URLs, paths, and settings are hardcoded throughout
7. **Performance**: All data loads on app startup, even if user only needs one equipment type

### Migration Goals
1. **Modularity**: Break down the monolith into focused, single-responsibility modules
2. **Reusability**: Create shared components that work across all equipment types
3. **Scalability**: Make it easy to add new equipment types without code duplication
4. **Maintainability**: Clear separation of concerns for easier debugging and updates
5. **Testability**: Enable unit testing of individual components
6. **Performance**: Implement lazy loading to improve startup time
7. **Developer Experience**: Clear project structure that new developers can understand quickly

### Expected Benefits

#### For Development
- **Faster Feature Development**: Add new equipment types in hours, not days
- **Easier Debugging**: Issues isolated to specific modules
- **Better Collaboration**: Multiple developers can work on different components
- **Code Quality**: Type hints and tests prevent regressions

#### For Deployment
- **Railway Compatibility**: Maintained and improved with dedicated deployment folder
- **Environment Management**: Easy switching between dev/staging/production
- **Resource Efficiency**: Lazy loading reduces memory usage

#### For Users
- **Faster Load Times**: Only load data for the equipment type being viewed
- **Consistent Experience**: Shared components ensure uniform behavior
- **Better Error Messages**: Proper error handling throughout
- **No Feature Loss**: All current functionality preserved

### Architecture Principles
1. **DRY (Don't Repeat Yourself)**: Extract common patterns into reusable components
2. **SOLID Principles**: Single responsibility, open for extension
3. **Separation of Concerns**: Data, business logic, and UI are separate layers
4. **Configuration over Code**: Settings externalized to config files
5. **Progressive Enhancement**: Each phase adds value without breaking existing features

### Risk Mitigation
- **Incremental Migration**: Three phases allow testing between major changes
- **Comprehensive Testing**: Checklist ensures nothing breaks
- **Path Mapping**: Detailed old→new path reference prevents broken imports
- **Rollback Plan**: Git branches allow easy reversion if needed

## Overview
This document outlines the complete migration plan from the current monolithic structure to a modular, scalable architecture.

## Phase 1: Project Restructuring (No Functionality Changes)

### 1.1 Create New Directory Structure
- [ ] Create `app/` directory
- [ ] Create `app/pages/` directory
- [ ] Create `app/components/` directory
- [ ] Create `app/utils/` directory
- [ ] Create `data/` directory
- [ ] Create `data/downloaders/` directory
- [ ] Create `data/models/` directory
- [ ] Create `deployment/` directory
- [ ] Create `tests/` directory
- [ ] Create all `__init__.py` files

### 1.2 Move and Refactor Main Application
- [ ] Split `solar_explorer.py` into modular components:
  - [ ] Extract main app setup to `app/main.py`
  - [ ] Extract PV modules logic to `app/pages/pv_modules.py`
  - [ ] Extract inverters logic to `app/pages/inverters.py`
  - [ ] Extract energy storage logic to `app/pages/energy_storage.py`
  - [ ] Extract batteries logic to `app/pages/batteries.py`
  - [ ] Extract meters logic to `app/pages/meters.py`

### 1.3 Extract Reusable Components
- [ ] Create `app/components/filters.py` (extract filter functionality)
- [ ] Create `app/components/visualizations.py` (extract chart functions)
- [ ] Create `app/components/comparisons.py` (extract comparison logic)
- [ ] Create `app/components/statistics.py` (extract stats display)

### 1.4 Create Utility Modules
- [ ] Create `app/utils/database.py` (database connection management)
- [ ] Create `app/utils/data_loader.py` (data loading functions)
- [ ] Create `app/utils/formatters.py` (date formatting functions)
- [ ] Create `app/config.py` (configuration management)

### 1.5 Reorganize Downloaders
- [ ] Create `data/downloaders/base_downloader.py` (abstract base class)
- [ ] Move `modules/pv_module_downloader.py` to `data/downloaders/`
- [ ] Move `inverters/inverter_downloader.py` to `data/downloaders/`
- [ ] Move `storage/energy_storage_downloader.py` to `data/downloaders/`
- [ ] Move `batteries/battery_downloader.py` to `data/downloaders/`
- [ ] Move `meters/meter_downloader.py` to `data/downloaders/`
- [ ] Update all database save paths in downloaders to use `db/` directory

### 1.6 Move Deployment Files
- [ ] Move `railway.toml` to `deployment/`
- [ ] Move `railway.json` to `deployment/`
- [ ] Move `Procfile` to `deployment/`
- [ ] Update `start_app.py` to reference new app structure
- [ ] Move `start_app.py` to `scripts/`

### 1.7 Update File Paths
- [ ] Update `setup.py` downloader paths:
  - `modules/pv_module_downloader.py` → `data/downloaders/pv_module_downloader.py`
  - `inverters/inverter_downloader.py` → `data/downloaders/inverter_downloader.py`
  - `storage/energy_storage_downloader.py` → `data/downloaders/energy_storage_downloader.py`
  - `batteries/battery_downloader.py` → `data/downloaders/battery_downloader.py`
  - `meters/meter_downloader.py` → `data/downloaders/meter_downloader.py`
- [ ] Update `solar_explorer.py` (now `app/main.py`) downloader paths
- [ ] Update database paths in all downloaders to use `db/` directory
- [ ] Update `start_app.py` to run `app.main:main()` instead of `solar_explorer.py`
- [ ] Update `Procfile` to reference new `scripts/start_app.py` location

### 1.8 Clean Up Old Structure
- [ ] Remove empty `modules/` directory
- [ ] Remove empty `inverters/` directory
- [ ] Remove empty `storage/` directory
- [ ] Remove empty `batteries/` directory
- [ ] Remove empty `meters/` directory
- [ ] Move existing utils scripts to `app/utils/` or `scripts/`

### 1.9 Update Configuration Files
- [ ] Update `.gitignore` to include new paths
- [ ] Create `.env.example` with configuration template
- [ ] Update `requirements.txt` if needed
- [ ] Update `README.md` with new structure documentation

## Phase 2: Code Improvements

### 2.1 Implement Base Classes
- [ ] Implement `BaseDownloader` abstract class
- [ ] Refactor all downloaders to inherit from `BaseDownloader`
- [ ] Create equipment data models in `data/models/equipment.py`

### 2.2 Implement Configuration Management
- [ ] Create environment variable support in `app/config.py`
- [ ] Move hardcoded URLs to configuration
- [ ] Add database configuration settings
- [ ] Add UI configuration settings

### 2.3 Improve Error Handling
- [ ] Add proper logging throughout the application
- [ ] Implement graceful error handling in downloaders
- [ ] Add user-friendly error messages

### 2.4 Add Type Hints
- [ ] Add type hints to all functions
- [ ] Create type definitions for data structures
- [ ] Add docstrings to all modules and functions

## Phase 3: Performance Optimizations

### 3.1 Implement Lazy Loading
- [ ] Load data only when specific page is accessed
- [ ] Implement proper Streamlit session state management
- [ ] Optimize database queries

### 3.2 Improve Caching
- [ ] Implement TTL-based caching for data
- [ ] Add cache invalidation mechanisms
- [ ] Optimize Streamlit cache usage

### 3.3 Database Optimizations
- [ ] Add proper indexes to SQLite databases
- [ ] Implement connection pooling
- [ ] Add database migration support

## Testing Checklist

### After Each Phase
- [ ] Verify all equipment types load correctly
- [ ] Test data downloading functionality
- [ ] Verify all visualizations work
- [ ] Test filtering functionality
- [ ] Test comparison features
- [ ] Verify Railway deployment still works
- [ ] Check that all file paths are correct
- [ ] Ensure no broken imports

## File Path Updates Reference

### Old Path → New Path
```
solar_explorer.py → app/main.py
start_app.py → scripts/start_app.py
setup.py → scripts/setup.py
modules/pv_module_downloader.py → data/downloaders/pv_module_downloader.py
inverters/inverter_downloader.py → data/downloaders/inverter_downloader.py
storage/energy_storage_downloader.py → data/downloaders/energy_storage_downloader.py
batteries/battery_downloader.py → data/downloaders/battery_downloader.py
meters/meter_downloader.py → data/downloaders/meter_downloader.py
railway.toml → deployment/railway.toml
railway.json → deployment/railway.json
Procfile → deployment/Procfile
utils/* → app/utils/* or scripts/*
db/*.db → db/*.db (no change)
```

## Critical Path Updates

### In `scripts/setup.py`:
```python
# Old
base_dir / "modules" / "pv_module_downloader.py"
# New
base_dir / "data" / "downloaders" / "pv_module_downloader.py"
```

### In `scripts/start_app.py`:
```python
# Old
subprocess.run([sys.executable, "-m", "streamlit", "run", "solar_explorer.py"])
# New
subprocess.run([sys.executable, "-m", "streamlit", "run", "app/main.py"])
```

### In `deployment/Procfile`:
```
# Old
web: python start_app.py
# New
web: python scripts/start_app.py
```

### In all downloaders:
```python
# Old
with sqlite3.connect('equipment.db') as conn:
# New
with sqlite3.connect('db/equipment.db') as conn:
```

## Success Criteria
- [ ] Application runs without errors
- [ ] All data loads correctly
- [ ] All features work as before
- [ ] Railway deployment succeeds
- [ ] Code is more maintainable and organized
- [ ] No functionality is lost

## Code Examples: Before vs After

### Adding a New Equipment Type

#### Before (Monolithic)
```python
# In solar_explorer.py - Need to add 100+ lines of code
with tab6:
    # Copy-paste entire block from another tab
    # Modify column names
    # Hope you didn't miss anything
```

#### After (Modular)
```python
# 1. Create app/pages/new_equipment.py
from app.components import display_equipment_page

def show():
    display_equipment_page(
        equipment_type="New Equipment",
        data_loader=load_new_equipment_data,
        columns=NEW_EQUIPMENT_COLUMNS
    )

# 2. Add to app/main.py
pages = {
    "New Equipment": new_equipment.show
}

# 3. Create data/downloaders/new_equipment_downloader.py
from data.downloaders.base_downloader import BaseDownloader

class NewEquipmentDownloader(BaseDownloader):
    url = "https://..."
    equipment_type = "new_equipment"
```

### Modifying Filter Behavior

#### Before
```python
# Need to update filter code in 5 different places in solar_explorer.py
```

#### After
```python
# Update once in app/components/filters.py
def create_filters(df, equipment_type):
    # Modified behavior applies everywhere
```

## Quick Reference for Developers

### Where to Find Things
- **UI Components**: `app/components/`
- **Page Logic**: `app/pages/`
- **Data Loading**: `app/utils/data_loader.py`
- **Database Connections**: `app/utils/database.py`
- **Configuration**: `app/config.py`
- **Downloaders**: `data/downloaders/`
- **Deployment**: `deployment/`

### Common Tasks
1. **Add new equipment type**: Create new page in `app/pages/` and downloader in `data/downloaders/`
2. **Modify UI component**: Edit relevant file in `app/components/`
3. **Change data source URL**: Update in `app/config.py`
4. **Add new visualization**: Add to `app/components/visualizations.py`
5. **Update deployment**: Modify files in `deployment/`

### Testing Locally
```bash
# After migration
cd solar-equipment-explorer-v2
python scripts/setup.py  # Download all data
streamlit run app/main.py  # Run the app
```

### Deployment Commands
```bash
# Railway deployment remains the same
railway up
```

## Migration Timeline Estimate
- **Phase 1**: 2-3 hours (mechanical refactoring)
- **Phase 2**: 3-4 hours (implementing improvements)
- **Phase 3**: 2-3 hours (performance optimizations)
- **Testing**: 1-2 hours (comprehensive testing)

Total: ~10-12 hours for complete migration

## Notes for Future Maintainers
1. The modular structure allows for easy extension - follow the established patterns
2. All equipment types share the same base components - changes propagate automatically
3. Configuration is centralized - no need to hunt for hardcoded values
4. Tests ensure stability - always run tests before deploying
5. The architecture supports future enhancements like API endpoints, data export, etc.
