# Cosmere DM MCP Server Roadmap

## Design Philosophy: This MCP extends a Dungeon Master (DM) AI's ability to parse Coppermind wiki pages and cache results into "cliff notes cards" it can refer to later.
This saves it from having to search for an retireve multiple pages, then reason through them eveery time.
As the AI uses the MCP server it will accumulate "cards" (json files) that store the results of common actions.

Workflow Example: AI Agent Needs Info
1. AI Identifies it needs to understand how the (Nalthian) Awakening **magic system** works.
2. Checks for a card about Awakening
3. If none exists, it searches the wiki and parses articles and creates a structured card with the relevant information.
4. This also allows the AI to store information that players experienced in the Cosmere provide, for use across sessions and different chat threads it would otherwise later lose.

Workflow Example: Knowledgeable Player Corrects AI's Understanding
1. Either look up recently used card by ID, or search for the card with faulty knowledge (e.g. MagicSystem: Awakening)
2. AI reads card and edits it to store the information the player provided

Challenges and Mitigations:
A. How to fix cards if they are incorrect
   - Version cards with timestamps for rollback capability
   - Allow manual card editing/deletion through MCP functions
   - Confidence scoring on card contents (0.0-1.0 scale)
   - Usage counters - track how often cards are referenced/edited to identify high-value vs. temporal information
B. How to update the information on cards if info on the wiki changes
   - Expiration dates on cards (configurable per card type)
   - Wiki change detection (compare page timestamps)
   - Manual refresh commands to rebuild cards from latest wiki content
   - Version comparison tools to show what changed between card versions
C. Card Type Proliferation
   - AI agents can create custom card types, but system tracks usage
   - Scheduled review process to identify low-usage custom card types
   - Consolidation recommendations: merge rarely-used types into general categories
   - Prevent card type explosion while maintaining AI flexibility

## Card Type Architecture

**Base Card Type** (all cards inherit from this):
```json
{
  "id": "unique_identifier",
  "type": "card_type",
  "title": "Human readable name",
  "usage_count": 0,
  "confidence": 0.9,
  "created": "2024-01-15T10:30:00Z",
  "updated": "2024-01-15T10:30:00Z",
  "sources": ["coppermind_page_urls"],
  "tags": ["optional", "categorization"],
  "notes": "AI-generated summary"
}
```

**Specific Card Types**:
- **MagicSystem**: mechanics, costs, limitations, investiture_type
- **Character**: timeline, relationships, abilities, current_status
- **Place**: geography, culture, politics, notable_locations
- **Concept**: principles, theories, cross_references (for realmatic physics, philosophical concepts)
- **Event**: timeline, participants, consequences, significance
- **Organization**: structure, goals, members, current_status

**AI-Generated Card Types**:
- AI agents can create new card types as needed
- System tracks usage of custom card types
- Periodic review consolidates low-usage custom types into general types

**Realmatic Physics Example**: 
- **Type**: `Concept`
- **Specialization**: Theoretical framework affecting multiple magic systems
- **Cross-references**: Links to magic systems it influences

## Storage Structure
Human readable for local use/MVP:

/.cosmere_dm/cards/
├── MagicSystem/
│   └── awakening.json
├── Character/
│   └── kaladin.json
├── Place/
│   └── urithiru.json
└── Concept/
    └── realmatic_physics.json


## Roadmap

**Phase 0: POC**
- [X] **search(query, limit)** - keyword search with structured results
- [X] **get_page(title)** - full page content with HTML, categories, links
- [X] **get_server_info()** - server metadata and capabilities

**Phase 1: Testing Framework**
- [X] **AI-testable framework** - pytest-based validation system
- [X] **Test fixtures** - known Cosmere facts for validation
- [X] **Error handling** - graceful degradation for failed requests
- [X] **Basic retrieval** - search() and get_page() working reliably with Coppermind

**Phase 2: Project Independence**
- [ ] Break away from upstream MediaWiki MCP repo
- [ ] Rename project to "Keeper MCP" (working title) - We're pulling information out of the Coppermind... :)
- [ ] Update README, documentation, and package metadata
- [ ] Set up independent repository and version control

**Phase 3: Core Card System**
- [ ] Design card storage structure (`~/.cosmere_dm/cards/`)
- [ ] `create_card(type, data)` - Create new cards with usage tracking
- [ ] `get_card(id)` - Retrieve card (increments usage_count)
- [ ] `update_card(id, data)` - Modify existing cards
- [ ] `delete_card(id)` - Remove cards
- [ ] `search_cards(query, type=None)` - Find cards by content/tags
- [ ] `list_cards(type=None)` - List all cards, optionally filtered

**Phase 4: Card Type Management**
- [ ] `create_card_type(name, schema)` - AI can define new card types
- [ ] `list_card_types()` - Show all available card types
- [ ] `get_card_type_usage(type)` - Usage statistics for card types
- [ ] `consolidate_card_types()` - Merge low-usage types into general categories

**Phase 5: Card Maintenance**
- [ ] `refresh_card(id)` - Rebuild card from latest wiki sources
- [ ] `validate_card(id)` - Check card against current wiki content
- [ ] `get_popular_cards()` - Show high usage_count cards
- [ ] `cleanup_unused_cards()` - Remove cards with very low usage

**Phase 6: Advanced Features**
- [ ] `find_related_cards(id)` - Discover connections between cards
- [ ] `export_cards(format)` - Export card collection for backup/sharing
- [ ] `import_cards(data)` - Import card collection from backup

## Success Metrics
- **Card Hit Rate**: >70% of queries use existing cards vs. fresh wiki lookups
- **Response Time**: <0.5 seconds for card retrieval, <3 seconds for card creation
- **Storage Efficiency**: Average card saves 2+ wiki page retrievals
- **User Satisfaction**: AI DM finds cards genuinely helpful for session continuity