import sys
import json
import ezdxf
from ezdxf import recover
import math
import re

def get_electrical_layer_info(layers):
    """Identify electrical-related layers"""
    electrical_keywords = [
        'electrical', 'elec', 'power', 'light', 'switch', 'outlet', 
        'wire', 'cable', 'panel', 'circuit', 'breaker', 'socket'
    ]
    
    electrical_layers = []
    for layer_name in layers:
        layer_lower = layer_name.lower()
        for keyword in electrical_keywords:
            if keyword in layer_lower:
                electrical_layers.append({
                    'name': layer_name,
                    'type': keyword,
                    'electrical': True
                })
                break
        else:
            electrical_layers.append({
                'name': layer_name,
                'type': 'general',
                'electrical': False
            })
    
    return electrical_layers

def classify_entity_type(entity):
    """Classify DXF entity into electrical component types"""
    dxftype = entity.dxftype()
    
    # Basic classifications based on entity type and properties
    if dxftype == 'CIRCLE':
        radius = entity.dxf.radius
        if 0.1 <= radius <= 0.5:
            return 'outlet'
        elif 0.5 < radius <= 1.0:
            return 'light_fixture'
        else:
            return 'general_circle'
    
    elif dxftype == 'INSERT':  # Block references (often electrical symbols)
        block_name = entity.dxf.name.lower() if hasattr(entity.dxf, 'name') else 'unknown'
        
        if any(keyword in block_name for keyword in ['switch', 'sw']):
            return 'switch'
        elif any(keyword in block_name for keyword in ['outlet', 'socket', 'receptacle']):
            return 'outlet'
        elif any(keyword in block_name for keyword in ['light', 'lamp', 'fixture']):
            return 'light'
        elif any(keyword in block_name for keyword in ['panel', 'board']):
            return 'electrical_panel'
        else:
            return 'electrical_symbol'
    
    elif dxftype == 'LINE':
        return 'wire'
    
    elif dxftype == 'POLYLINE' or dxftype == 'LWPOLYLINE':
        return 'wire_path'
    
    elif dxftype == 'TEXT' or dxftype == 'MTEXT':
        return 'annotation'
    
    elif dxftype == 'RECTANGLE':
        return 'panel'
    
    else:
        return 'general'

def extract_entity_properties(entity):
    """Extract relevant properties from DXF entity"""
    properties = {
        'type': entity.dxftype(),
        'layer': getattr(entity.dxf, 'layer', 'unknown'),
        'color': getattr(entity.dxf, 'color', 'bylayer')
    }
    
    # Position information
    if hasattr(entity.dxf, 'insert'):  # Block reference
        properties['position'] = [entity.dxf.insert.x, entity.dxf.insert.y]
        properties['rotation'] = getattr(entity.dxf, 'rotation', 0)
        properties['scale'] = [
            getattr(entity.dxf, 'xscale', 1),
            getattr(entity.dxf, 'yscale', 1)
        ]
    elif hasattr(entity.dxf, 'center'):  # Circle
        properties['center'] = [entity.dxf.center.x, entity.dxf.center.y]
        properties['radius'] = entity.dxf.radius
    elif hasattr(entity.dxf, 'start'):  # Line
        properties['start'] = [entity.dxf.start.x, entity.dxf.start.y]
        properties['end'] = [entity.dxf.end.x, entity.dxf.end.y]
        properties['length'] = math.sqrt(
            (entity.dxf.end.x - entity.dxf.start.x)**2 + 
            (entity.dxf.end.y - entity.dxf.start.y)**2
        )
    
    # Text content
    if entity.dxftype() in ['TEXT', 'MTEXT']:
        properties['text'] = getattr(entity.dxf, 'text', '')
        properties['height'] = getattr(entity.dxf, 'height', 0)
    
    # Block reference name
    if entity.dxftype() == 'INSERT':
        properties['block_name'] = getattr(entity.dxf, 'name', '')
    
    return properties

def analyze_electrical_connections(entities):
    """Analyze potential electrical connections between components"""
    wires = [e for e in entities if e['classification'] in ['wire', 'wire_path']]
    components = [e for e in entities if e['classification'] in 
                 ['switch', 'outlet', 'light', 'electrical_panel']]
    
    connections = []
    
    for wire in wires:
        wire_props = wire['properties']
        connected_components = []
        
        # Check if wire endpoints are near components
        if 'start' in wire_props and 'end' in wire_props:
            start_point = wire_props['start']
            end_point = wire_props['end']
            
            for comp in components:
                comp_props = comp['properties']
                comp_pos = None
                
                if 'position' in comp_props:
                    comp_pos = comp_props['position']
                elif 'center' in comp_props:
                    comp_pos = comp_props['center']
                
                if comp_pos:
                    # Check if component is near wire endpoints (within 1 unit)
                    start_dist = math.sqrt(
                        (start_point[0] - comp_pos[0])**2 + 
                        (start_point[1] - comp_pos[1])**2
                    )
                    end_dist = math.sqrt(
                        (end_point[0] - comp_pos[0])**2 + 
                        (end_point[1] - comp_pos[1])**2
                    )
                    
                    if start_dist < 1.0 or end_dist < 1.0:
                        connected_components.append({
                            'component_id': comp['id'],
                            'component_type': comp['classification'],
                            'distance': min(start_dist, end_dist)
                        })
        
        if connected_components:
            connections.append({
                'wire_id': wire['id'],
                'connected_components': connected_components
            })
    
    return connections

def parse_dxf(file_path):
    """Main DXF parsing function"""
    try:
        # Try to read the DXF file
        try:
            doc = ezdxf.readfile(file_path)
        except IOError:
            print(f"Not a DXF file or a generic I/O error.", file=sys.stderr)
            return {'error': 'Not a valid DXF file'}
        except ezdxf.DXFStructureError:
            print(f"Invalid or corrupted DXF file.", file=sys.stderr)
            return {'error': 'Invalid or corrupted DXF file'}
        
        # Get modelspace
        msp = doc.modelspace()
        
        # Get layer information
        layers = [layer.dxf.name for layer in doc.layers]
        layer_info = get_electrical_layer_info(layers)
        
        # Process entities
        entities = []
        entity_id = 0
        
        for entity in msp:
            entity_data = {
                'id': entity_id,
                'classification': classify_entity_type(entity),
                'properties': extract_entity_properties(entity)
            }
            entities.append(entity_data)
            entity_id += 1
        
        # Analyze electrical connections
        connections = analyze_electrical_connections(entities)
        
        # Generate summary statistics
        stats = {
            'total_entities': len(entities),
            'electrical_entities': len([e for e in entities if e['classification'] != 'general']),
            'layers': len(layers),
            'electrical_layers': len([l for l in layer_info if l['electrical']]),
            'connections': len(connections)
        }
        
        # Categorize entities by type
        entity_categories = {}
        for entity in entities:
            category = entity['classification']
            if category not in entity_categories:
                entity_categories[category] = []
            entity_categories[category].append(entity)
        
        return {
            'entities': entities,
            'entity_categories': entity_categories,
            'layer_info': layer_info,
            'connections': connections,
            'statistics': stats,
            'drawing_info': {
                'units': doc.header.get('$INSUNITS', 'unknown'),
                'version': doc.dxfversion,
                'created_by': doc.header.get('$ACADVER', 'unknown')
            },
            'analysis_type': 'dxf_electrical_plan'
        }
        
    except Exception as e:
        return {
            'error': f"DXF parsing failed: {str(e)}",
            'entities': [],
            'entity_categories': {},
            'layer_info': [],
            'connections': [],
            'statistics': {}
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'File path required'}))
        sys.exit(1)
    
    file_path = sys.argv[1]
    data = parse_dxf(file_path)
    print(json.dumps(data, indent=2))
