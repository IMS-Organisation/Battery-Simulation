"""
File: ui.py
Author: F. Bisinger, E. Grenz, I. Schopf
Date: 2024-04-29
Description: BatteryCT Blender UI + Cell generation
"""

import bpy
import json
import numpy as np
import os
from datetime import datetime
import bmesh

# ------------------------------------------------------------------------
#    Properties Battery Modeling
# ------------------------------------------------------------------------

class Modeling:
    
    def __init__(self):
        # All lengths in m (SI)
        self.iterations = 1
        self.seperator_height = 0.001 
        self.anode_overhang_bool = True
        self.export_inner_battery_bool = True
        self.export_housing_bool = True
        self.cut_housing_zy_bool = True
        self.cut_housing_zx_bool = True
        self.bending_bool = True
        
        self.max_angle = 15.0
        self.min_angle = -15.0

        self.x_variation = 1e-3
        self.y_variation = 1e-3

        # create time stamp for export
        self.current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.export_folder = os.path.normpath("Model_" + self.current_datetime)
        self.export_path = os.path.join(r"C:/", self.export_folder)

        self.anode = {
            "length": 0.1015,
            "width": 0.050,
            "height": 0.001, 
            "length_tol": 0.000,
            "max_overhang": 0.0068,
            "min_overhang": 0.0023,
            "width_tol": 0.000,
            "height_tol": 0.000,
            "amount": 10 , # integer
            "color": (1, 0, 0, 1),  # red color (RGB values)
        }

        self.lower_anode_coating = {
            "length": 0.1015,
            "width": 0.050,
            "height": 0.05,
            "length_tol": 0.000,
            "max_overhang": self.anode["max_overhang"],
            "min_overhang": self.anode["min_overhang"],
            "width_tol": 0.000,
            "height_tol": 0.000,
            "amount": self.anode["amount"],
            "color": (0, 0, 0, 1),  # black color (RGB values)
        }

        self.upper_anode_coating = {
            "length": 0.1015,
            "width": 0.050,
            "height": 0.05,
            "length_tol": 0.000,
            "max_overhang": self.anode["max_overhang"],
            "min_overhang": self.anode["min_overhang"],
            "width_tol": 0.000,
            "height_tol": 0.000,
            "amount": self.anode["amount"],
            "color": (0, 0, 0, 1),  # black color (RGB values)
        }

        self.cathode = {
            "length": 0.1015,
            "width": 0.050,
            "height": 0.001, 
            "length_tol": 0.000,
            "width_tol": 0.000,
            "height_tol": 0.000,
            "amount": self.anode["amount"]-1, # integer
            "color": (0, 1, 0, 1),  # green color (RGB values)
        }

        self.lower_cathode_coating = {
            "length": 0.1015,
            "width": 0.050,
            "height": 0.001,
            "length_tol": 0.000,
            "width_tol": 0.000,
            "height_tol": 0.000,
            "amount": self.anode["amount"]-1,
            "color": (0, 0, 1, 1),  # blue color (RGB values)
        }

        self.upper_cathode_coating = {
            "length": 0.1015,
            "width": 0.050,
            "height": 0.001,
            "length_tol": 0.000,
            "width_tol": 0.000,
            "height_tol": 0.000,
            "amount": self.anode["amount"]-1,
            "color": (0, 0, 1, 1),  # blue color (RGB values)
        }

        # END VARIABLE PARAMETERSET

        self.housing_geometry = {
            # battery sizes
            "outer_width": (self.anode["width"] + self.y_variation*2 + 0.008), 
            "outer_length": (self.anode["length"] + self.anode["max_overhang"] + self.x_variation*2 + 0.008),  
            "wall_thickness": 0.001
        }

        self.anode["overhang"] = {
         # GIBT EINE ZUFÄLLIGE GLEITKOMMAZAHL IN DIESEM BEREICH ZURÜCK
         "anode_overhang": np.random.uniform(self.anode["min_overhang"], self.anode["max_overhang"])
        }

        # Formula for parametric positioning
        self.anode["position"] = {
            "z_position": ((self.anode["height"]/2.0) + (self.lower_anode_coating["height"])+self.seperator_height + (self.housing_geometry["wall_thickness"]/2.0)),
            "z_distance": self.anode["height"]+self.cathode["height"]+2*self.seperator_height+self.upper_anode_coating["height"]+self.lower_anode_coating["height"]+self.upper_cathode_coating["height"]+self.lower_cathode_coating["height"]
        }

        self.lower_anode_coating["position"] = {
            "z_position": self.anode["position"]["z_position"]-((self.anode["height"] + self.lower_anode_coating["height"]) / 2.0),
            "z_distance": self.anode["position"]["z_distance"]
        }

        self.upper_anode_coating["position"] = {
            "z_position": self.anode["position"]["z_position"]+((self.anode["height"] + self.upper_anode_coating["height"]) / 2.0),
            "z_distance": self.anode["position"]["z_distance"]
        }

        self.cathode["position"] = {
            "z_position": self.anode["position"]["z_position"]+(((self.anode["height"]+self.cathode["height"])/2)+self.upper_anode_coating["height"]+self.lower_cathode_coating["height"]+self.seperator_height),
            "z_distance": self.anode["height"]+self.cathode["height"]+2*self.seperator_height+self.upper_anode_coating["height"]+self.lower_anode_coating["height"]+self.upper_cathode_coating["height"]+self.lower_cathode_coating["height"]
        }

        self.lower_cathode_coating["position"] = {
            "z_position": (self.cathode["position"]["z_position"]-((self.cathode["height"]+self.lower_cathode_coating["height"])/2.0)),
            "z_distance": self.cathode["position"]["z_distance"]
        }

        self.upper_cathode_coating["position"] = {
            "z_position": (self.cathode["position"]["z_position"]+((self.cathode["height"]+self.lower_cathode_coating["height"])/2.0)),
            "z_distance": self.cathode["position"]["z_distance"]
        }

        self.housing_geometry["more_geometry"] = {
            "bevel_radius": 1,
            "outer_height": (self.anode["amount"]*self.anode["height"]) + (self.cathode["amount"]*self.cathode["height"]) + (self.lower_anode_coating["amount"]*self.lower_anode_coating["height"]) + (self.upper_anode_coating["amount"]*self.upper_anode_coating["height"]) + (self.lower_cathode_coating["amount"]*self.lower_cathode_coating["height"]) + (self.upper_cathode_coating["amount"]*self.upper_cathode_coating["height"]) + (2*self.anode["amount"]*self.seperator_height)+(self.housing_geometry["wall_thickness"]), 
        }
        
        self.data = {
            "anode": {
                "anode_position": {"x": [], "y": [], "z": []},
                "anode_dimensions": {"length": [], "width": [], "height": []},
                "anode_deviations": {"length": [],"width": [], "height": [], "x_position": [], "y_position": []},
                "anode_bending": {"x+": [], "x-":[]}
            },
            "cathode": {
                "cathode_position": {"x": [], "y": [], "z": []},
                "cathode_dimensions": {"length": [], "width": [], "height": []},
                "cathode_deviations": {"length": [],"width": [], "height": [], "x_position": [], "y_position": []},
                "cathode_bending": {"x+": [], "x-":[]}
            },
            "housing": {
                "housing_position": {"x": [], "y": [], "z": []},
                "housing_dimensions": {"outer_length": [], "outer_width": [], "outer_height": [], "inner_length": [],"inner_width": [],"inner_height": []}
            },
            "upper_cathode_coating": {
                "upper_cathode_coating_position": {"x": [], "y": [], "z": []},
                "upper_cathode_coating_dimensions": {"length": [], "width": [], "height": []},
                "upper_cathode_coating_deviations": {"length": [],"width": [], "height": [], "x_position": [], "y_position": []}
            },
            "lower_cathode_coating": {
                "lower_cathode_coating_position": {"x": [], "y": [], "z": []},
                "lower_cathode_coating_dimensions": {"length": [], "width": [], "height": []},
                "lower_cathode_coating_deviations": {"length": [],"width": [], "height": [], "x_position": [], "y_position": []}
            },
            "upper_anode_coating": {
                "upper_anode_coating_position": {"x": [], "y": [], "z": []},
                "upper_anode_coating_dimensions": {"length": [], "width": [], "height": []},
                "upper_anode_coating_deviations": {"length": [],"width": [], "height": [], "x_position": [], "y_position": []}
            },
            "lower_anode_coating": {
                "lower_anode_coating_position": {"x": [], "y": [], "z": []},
                "lower_anode_coating_dimensions": {"length": [], "width": [], "height": []},
                "lower_anode_coating_deviations": {"length": [],"width": [], "height": [], "x_position": [], "y_position": []}
            }
        }
        
        
                    
        
        print("PARAMS INIT DONE")


    ######################################## FUNCTIONS START ########################################
    def create_and_export_inner_battery(self, j, parameters, name):
            
        for i in range(parameters["amount"]):

            deviations = self.generate_deviations(parameters, self.x_variation, self.y_variation)
            
            # Adjust x and y position if upper or lower anode/cathode coating
            if parameters in [self.lower_anode_coating, self.upper_anode_coating]:
                x_position = self.data["anode"]["anode_position"]["x"][i]  # Get x position from the anode position list
                y_position = self.data["anode"]["anode_position"]["y"][i]  # Get y position from the anode position list
            elif parameters in [self.lower_cathode_coating, self.upper_cathode_coating]:
                x_position = self.data["cathode"]["cathode_position"]["x"][i]  # Get x position from the cathode position list
                y_position = self.data["cathode"]["cathode_position"]["y"][i]  # Get y position from the cathode position list
            else:
                # Für den Fall, dass es eine Anode oder Kathode ist wird eine neue Position generiert
                x_position = deviations["x_position"]
                y_position = deviations["y_position"]
            
            z_position = parameters["position"]["z_position"] + i * (parameters["position"]["z_distance"])

            dimensions = self.generate_dimensions(name, parameters, deviations)
            actual_bending_plus = deviations["bending"]["x+"]
            actual_bending_minus = deviations["bending"]["x-"]
                        
            bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=(x_position, y_position, z_position))
            obj = bpy.context.object
            obj.name = f"{name}_{i}" 
            obj_name = str(obj.name)    

            # Positionsübergabe: Ziel: Position_Blech == Position_Beschichtung (x und y), z ist individuell!
            # Datentransfer für Labeling mit .json-file

            if name == "anode":
                    self.data["anode"]["anode_position"]["x"].append(x_position)
                    self.data["anode"]["anode_position"]["y"].append(y_position)
                    self.data["anode"]["anode_position"]["z"].append(z_position)
                    
                    self.data["anode"]["anode_dimensions"]["length"].append(dimensions["length"])
                    self.data["anode"]["anode_dimensions"]["width"].append(dimensions["width"])
                    self.data["anode"]["anode_dimensions"]["height"].append(dimensions["height"])
                    
                    self.data["anode"]["anode_deviations"]["length"].append(deviations["length"])
                    self.data["anode"]["anode_deviations"]["width"].append(deviations["width"])
                    self.data["anode"]["anode_deviations"]["height"].append(deviations["height"])
                    self.data["anode"]["anode_deviations"]["x_position"].append(deviations["x_position"])
                    self.data["anode"]["anode_deviations"]["y_position"].append(deviations["y_position"])
                    self.data["anode"]["anode_bending"]["x+"].append(actual_bending_plus)
                    self.data["anode"]["anode_bending"]["x-"].append(actual_bending_minus)
                    
            elif name == "cathode":
                    self.data["cathode"]["cathode_position"]["x"].append(x_position)
                    self.data["cathode"]["cathode_position"]["y"].append(y_position)
                    self.data["cathode"]["cathode_position"]["z"].append(z_position)
                    
                    self.data["cathode"]["cathode_dimensions"]["length"].append(dimensions["length"])
                    self.data["cathode"]["cathode_dimensions"]["width"].append(dimensions["width"])
                    self.data["cathode"]["cathode_dimensions"]["height"].append(dimensions["height"])
                    
                    self.data["cathode"]["cathode_deviations"]["length"].append(deviations["length"])
                    self.data["cathode"]["cathode_deviations"]["width"].append(deviations["width"])
                    self.data["cathode"]["cathode_deviations"]["height"].append(deviations["height"])
                    self.data["cathode"]["cathode_deviations"]["x_position"].append(deviations["x_position"])
                    self.data["cathode"]["cathode_deviations"]["y_position"].append(deviations["y_position"])
                    self.data["cathode"]["cathode_bending"]["x+"].append(actual_bending_plus)
                    self.data["cathode"]["cathode_bending"]["x-"].append(actual_bending_minus)
   
            elif name == "upper_anode_coating":
                    self.data["upper_anode_coating"]["upper_anode_coating_position"]["x"].append(x_position)
                    self.data["upper_anode_coating"]["upper_anode_coating_position"]["y"].append(y_position)
                    self.data["upper_anode_coating"]["upper_anode_coating_position"]["z"].append(z_position)
                    
                    self.data["upper_anode_coating"]["upper_anode_coating_dimensions"]["length"].append(dimensions["length"])
                    self.data["upper_anode_coating"]["upper_anode_coating_dimensions"]["width"].append(dimensions["width"])
                    self.data["upper_anode_coating"]["upper_anode_coating_dimensions"]["height"].append(dimensions["height"])
                    
                    self.data["upper_anode_coating"]["upper_anode_coating_deviations"]["length"].append(deviations["length"])
                    self.data["upper_anode_coating"]["upper_anode_coating_deviations"]["width"].append(deviations["width"])
                    self.data["upper_anode_coating"]["upper_anode_coating_deviations"]["height"].append(deviations["height"])
                    self.data["upper_anode_coating"]["upper_anode_coating_deviations"]["x_position"].append(deviations["x_position"])
                    self.data["upper_anode_coating"]["upper_anode_coating_deviations"]["y_position"].append(deviations["y_position"])           
                    
            elif name == "lower_anode_coating":
                    self.data["lower_anode_coating"]["lower_anode_coating_position"]["x"].append(x_position)
                    self.data["lower_anode_coating"]["lower_anode_coating_position"]["y"].append(y_position)
                    self.data["lower_anode_coating"]["lower_anode_coating_position"]["z"].append(z_position)
                    
                    self.data["lower_anode_coating"]["lower_anode_coating_dimensions"]["length"].append(dimensions["length"])
                    self.data["lower_anode_coating"]["lower_anode_coating_dimensions"]["width"].append(dimensions["width"])
                    self.data["lower_anode_coating"]["lower_anode_coating_dimensions"]["height"].append(dimensions["height"])
                    
                    self.data["lower_anode_coating"]["lower_anode_coating_deviations"]["length"].append(deviations["length"])
                    self.data["lower_anode_coating"]["lower_anode_coating_deviations"]["width"].append(deviations["width"])
                    self.data["lower_anode_coating"]["lower_anode_coating_deviations"]["height"].append(deviations["height"])
                    self.data["lower_anode_coating"]["lower_anode_coating_deviations"]["x_position"].append(deviations["x_position"])
                    self.data["lower_anode_coating"]["lower_anode_coating_deviations"]["y_position"].append(deviations["y_position"])
                    
            elif name == "upper_cathode_coating":
                    self.data["upper_cathode_coating"]["upper_cathode_coating_position"]["x"].append(x_position)
                    self.data["upper_cathode_coating"]["upper_cathode_coating_position"]["y"].append(y_position)
                    self.data["upper_cathode_coating"]["upper_cathode_coating_position"]["z"].append(z_position)
                    
                    self.data["upper_cathode_coating"]["upper_cathode_coating_dimensions"]["length"].append(dimensions["length"])
                    self.data["upper_cathode_coating"]["upper_cathode_coating_dimensions"]["width"].append(dimensions["width"])
                    self.data["upper_cathode_coating"]["upper_cathode_coating_dimensions"]["height"].append(dimensions["height"])
                    
                    self.data["upper_cathode_coating"]["upper_cathode_coating_deviations"]["length"].append(deviations["length"])
                    self.data["upper_cathode_coating"]["upper_cathode_coating_deviations"]["width"].append(deviations["width"])
                    self.data["upper_cathode_coating"]["upper_cathode_coating_deviations"]["height"].append(deviations["height"])
                    self.data["upper_cathode_coating"]["upper_cathode_coating_deviations"]["x_position"].append(deviations["x_position"])
                    self.data["upper_cathode_coating"]["upper_cathode_coating_deviations"]["y_position"].append(deviations["y_position"])           
                    
            elif name == "lower_cathode_coating":
                    self.data["lower_cathode_coating"]["lower_cathode_coating_position"]["x"].append(x_position)
                    self.data["lower_cathode_coating"]["lower_cathode_coating_position"]["y"].append(y_position)
                    self.data["lower_cathode_coating"]["lower_cathode_coating_position"]["z"].append(z_position)
                    
                    self.data["lower_cathode_coating"]["lower_cathode_coating_dimensions"]["length"].append(dimensions["length"])
                    self.data["lower_cathode_coating"]["lower_cathode_coating_dimensions"]["width"].append(dimensions["width"])
                    self.data["lower_cathode_coating"]["lower_cathode_coating_dimensions"]["height"].append(dimensions["height"])
                    
                    self.data["lower_cathode_coating"]["lower_cathode_coating_deviations"]["length"].append(deviations["length"])
                    self.data["lower_cathode_coating"]["lower_cathode_coating_deviations"]["width"].append(deviations["width"])
                    self.data["lower_cathode_coating"]["lower_cathode_coating_deviations"]["height"].append(deviations["height"])
                    self.data["lower_cathode_coating"]["lower_cathode_coating_deviations"]["x_position"].append(deviations["x_position"])
                    self.data["lower_cathode_coating"]["lower_cathode_coating_deviations"]["y_position"].append(deviations["y_position"])
            else:
                # Sicherung im Zustandsautomaten
                print("Error: No objects found")
            
            
            obj.scale = (dimensions["length"], dimensions["width"], dimensions["height"])
            self.bend_object(obj_name, parameters, dimensions,  name, i)
         
            
            # Set color of the object
            obj.active_material = bpy.data.materials.new(name=f"Color_{j}_{i}")
            obj.active_material.diffuse_color = parameters["color"]

            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            # Objekt bennenen --> Relvant für die Auswahl des Objekts!


        # Export sequence
        self.export_inner_battery(name, i, j)

    # Funktion zum Biegen der Objekte    
    def bend_object(self, obj_name, type, dimensions, name, i):        
        if self.bending_bool == True:
            # Bending of elements
            
            if name == "anode" or name == "lower_anode_coating" or name == "upper_anode_coating":
                start_pos_z = self.data["anode"]["anode_position"]["z"][i]
                bending_x_pos = self.data["anode"]["anode_bending"]["x+"][i]
                bending_x_neg = self.data["anode"]["anode_bending"]["x-"][i]
            elif name == "cathode" or name == "lower_cathode_coating" or name == "upper_cathode_coating":
                start_pos_z = self.data["cathode"]["cathode_position"]["z"][i]
                bending_x_pos = self.data["cathode"]["cathode_bending"]["x+"][i]
                bending_x_neg = self.data["cathode"]["cathode_bending"]["x-"][i]
            else:
                print("Error: No bending positioning possible")                 
               
               
            obj = bpy.context.active_object
            mesh = obj.data
            
            # Get the active mesh object
            mesh = obj.data

            # Create a BMesh from the mesh
            bm = bmesh.new()
            bm.from_mesh(mesh)

            # Get edges to cut, here it's all edges of the mesh
            edges = bm.edges

            # Perform the loop cut
            bmesh.ops.subdivide_edges(bm, edges=edges, cuts=50, use_grid_fill=True)

            # Update the original mesh with the new data
            bm.to_mesh(mesh)
            bm.free()
            mesh.update()

            #Relative Positionen Bending
            relBendingposXpos=0.97
            relBendingposXneg=0.03
            ########## Vertex X+ ####################################################

            # Create a vertex group X+ Bending
            vertex_group = obj.vertex_groups.new(name='My Vertex Group')

            # Add vertices to the vertex group based on relative position
            for v in mesh.vertices:
                # Transform the vertex coordinate into world space
                world_vertex_co = obj.matrix_world @ v.co
                # Calculate the relative x position (from 0 to 1)
                relative_x = (world_vertex_co.x - obj.bound_box[0][0]) / (obj.bound_box[7][0] - obj.bound_box[0][0])
                # Check if the relative x-coordinate is between 0.8 and 1 (80% to 100% of the object's length)
                if relBendingposXpos <= relative_x <= 1:
                    vertex_group.add([v.index], 1.0, 'ADD')

            ########## Vertex Xneg ####################################################        

            # Create a vertex group X- Bending
            vertex_group = obj.vertex_groups.new(name='My Vertex Group Xneg')

            # Add vertices to the vertex group based on relative position
            for v in mesh.vertices:
                # Transform the vertex coordinate into world space
                world_vertex_co = obj.matrix_world @ v.co
                # Calculate the relative x position (from 0 to 1)
                relative_x = (world_vertex_co.x - obj.bound_box[0][0]) / (obj.bound_box[7][0] - obj.bound_box[0][0])
                # Check if the relative x-coordinate is between 0 and 0.2 (0% to 20% of the object's length)
                if 0 <= relative_x <= relBendingposXneg:
                    vertex_group.add([v.index], 1.0, 'ADD')

            # Switch back to Object Mode
            bpy.ops.object.mode_set(mode='OBJECT')

            # Calculate the start position of the vertex group in world space
            start_pos_x = (obj.bound_box[0][0] * dimensions["length"]) + relBendingposXpos * ((obj.bound_box[7][0] * dimensions["length"]) - (obj.bound_box[0][0] * dimensions["length"]))

            # Create an empty at the start position of the vertex group
            bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(start_pos_x, 0, start_pos_z))
            empty_xpos = bpy.context.object
            # Rotate Empty
            empty_xpos.rotation_euler[0] += 1.5708  # 90 degrees in radians (pi/2)
            bpy.context.view_layer.update()        
                

            # Calculate the start position of the vertex group neg in world space
            start_pos_xneg = (obj.bound_box[0][0] * dimensions["length"]) + relBendingposXneg * ((obj.bound_box[7][0] * dimensions["length"]) - (obj.bound_box[0][0] * dimensions["length"]))

            # Create an empty at the start position of the vertex group
            bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(start_pos_xneg, 0, start_pos_z))
            empty_xneg = bpy.context.object
            # Rotate Empty
            empty_xneg.rotation_euler[0] += 1.5708  # 90 degrees in radians (pi/2)
            bpy.context.view_layer.update()

            ########## Bending X+ ####################################################

            # Add Simple Deform Modifier to bend along the Z-axis using the empty as the origin
            modifier = obj.modifiers.new(name="Deform", type='SIMPLE_DEFORM')
            modifier.deform_method = 'BEND'
            modifier.origin = empty_xpos
            modifier.deform_axis = 'Z'

            # Assign the vertex group to the modifier
            modifier.vertex_group = 'My Vertex Group'

            # Set the angle of bending (in radians)            
            bend_angle = bending_x_pos * (np.pi)/180 * 360/45  # degrees in radians + scaling
            modifier.angle = bend_angle

            ########## Bending X- ####################################################

            # Add Simple Deform Modifier to bend along the Z-axis using the empty as the origin
            modifier = obj.modifiers.new(name="Deform", type='SIMPLE_DEFORM')
            modifier.deform_method = 'BEND'
            modifier.origin = empty_xneg
            modifier.deform_axis = 'Z'

            # Assign the vertex group to the modifier
            modifier.vertex_group = 'My Vertex Group Xneg'
            # Set the angle of bending (in radians)
            bend_angle2 = bending_x_neg * (np.pi)/180 * 360/45  #degrees in radians + scaling
            modifier.angle = bend_angle2
            
            
            ########## Decimate Modifier ####################################################

            # Add Decimate Modifier to reduce the number of vertices
            decimate_modifier = obj.modifiers.new(name="Decimate", type='DECIMATE')
            decimate_modifier.ratio = 0.1  # Adjust the ratio as needed (0.0 to 1.0)

            # Apply the Decimate Modifier
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier="Decimate")
            
            
            
                    
    # Funktion, um alle leeren Objekte im Raum vor neuem Programausführen löscht                
    def delete_empty_objects(self):
        # Filtere alle leeren Objekte heraus
        empty_objects = [obj for obj in bpy.data.objects if obj.type == 'EMPTY']
        
        # Lösche jedes leere Objekt
        for obj in empty_objects:
            bpy.data.objects.remove(obj, do_unlink=True)


    def export_inner_battery(self, name, ii, jj):
        if self.export_inner_battery_bool == True: 
            if not os.path.exists(self.export_path):
                os.makedirs(self.export_path)
                
                       
            bpy.ops.object.select_all(action='DESELECT')
            
            selected_objects = []
            
            for a in range(ii + 1):
                obj_name = f"{name}_{a}"
                obj = bpy.data.objects.get(obj_name)   
                
                if obj:
                    obj.select_set(True)
                    '''
####################Export Skalierung#####################################################################################################
                    # Skaliere das Objekt
                    bpy.ops.object.transform_apply(scale=True)  # Wende den Maßstab auf das Objekt an
                    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)  # Stelle sicher, dass alle Transformationen angewendet werden
                    
                    # Setze den Skalierungsfaktor
                    bpy.context.active_object.scale *=scale_factor
                    '''
                    
                    selected_objects.append(obj)
            
            if selected_objects:
                
                # Set export file path
                file_path = os.path.join(self.export_path, f"{jj+1}_{self.current_datetime}_{name}.stl")
                
                # Export the combined object as .stl file
                # GANZ WICHTIG: Letzter Teil im Code: use_selection=True
                # QUELLE: https://docs.blender.org/api/current/bpy.ops.export_scene.html
                bpy.ops.export_mesh.stl(filepath=file_path, check_existing=False, filter_glob="*.stl", ascii=False, use_selection=True)        
                # Deselect all objects after export
                bpy.ops.object.select_all(action='DESELECT')
                print(f"[{self.current_datetime}] Export of {name}_{jj+1} was successful, export path:\n{self.export_path}\n")
            else:
                print("No objects selected for export.")

    def generate_deviations(self, parameters, x_variation, y_variation):
        deviations = {
        # loc heißt Mittelwert und scale heißt Standardabweichung
            "length": np.random.normal(loc=0.0, scale=parameters["length_tol"]), # aktuell = 0 --> berücksichtigen bei Positionierung noch erforderlich!! 
            "width": np.random.normal(loc=0.0, scale=parameters["width_tol"]),   # aktuell = 0 --> berücksichtigen bei Positionierung noch erforderlich!! 
            "height": np.random.normal(loc=0.0, scale=parameters["height_tol"]), # aktuell = 0 --> berücksichtigen bei Positionierung noch erforderlich!! 
            "x_position": np.random.normal(loc=0.0, scale=x_variation),
            "y_position": np.random.normal(loc=0.0, scale=y_variation),
            "bending":
                {
                    "x+": np.random.uniform(self.min_angle, self.max_angle),
                    "x-": np.random.uniform(self.min_angle, self.max_angle)
                } 
        }
        return deviations

    def generate_dimensions(self, name, parameters, deviations):
        dimensions = {}
        
        if self.anode_overhang_bool == True:
            if name in ["anode", "lower_anode_coating", "upper_anode_coating"]:
                dimensions["length"] = max(0.001, parameters["length"] + deviations["length"] + self.anode["overhang"]["anode_overhang"])
            else:
                dimensions["length"] = max(0.001, parameters["length"] + deviations["length"])
        else:
            dimensions["length"] = max(0.001, parameters["length"] + deviations["length"])
        
        dimensions["width"] = max(0.001, parameters["width"] + deviations["width"])
        dimensions["height"] = max(0.001, parameters["height"] + deviations["height"])
        return dimensions

    def write_data_to_file(self, data, filename):
        self.data['Comment:'] = "All dimensions and deviations refer to the center point of the object.\nThe characteristic values for each element (1 to n) can be found below."
        full_path = os.path.join(self.export_path, filename)        
        with open(full_path, 'w') as file:
            json.dump(data, file, indent=4)
            

    def create_and_export_housing(self, housing_geometry, jj):
        # CREATE HOUSING
        # Create outer block
        x_loc = 0
        y_loc = 0
        z_loc = housing_geometry["more_geometry"]["outer_height"]/2.0
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_loc, y_loc, z_loc))
        outer_block = bpy.context.active_object
        outer_block.scale = (housing_geometry["outer_length"], housing_geometry["outer_width"], housing_geometry["more_geometry"]["outer_height"])

        # Create bevel edges for outer block
        bpy.context.view_layer.objects.active = outer_block
        bpy.context.object.name = f"housing_{jj}"
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.bevel(offset=housing_geometry["more_geometry"]["bevel_radius"], segments=4)
        bpy.ops.object.mode_set(mode='OBJECT')

        # Create inner block
        inner_width = housing_geometry["outer_width"] - housing_geometry["wall_thickness"]
        inner_height = housing_geometry["more_geometry"]["outer_height"] - housing_geometry["wall_thickness"]
        inner_length = housing_geometry["outer_length"] - housing_geometry["wall_thickness"]
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, housing_geometry["more_geometry"]["outer_height"]/2.0))
        inner_block = bpy.context.active_object
        inner_block.scale = (inner_length, inner_width, inner_height)

        # Create bevel edges for inner block
        bpy.context.view_layer.objects.active = inner_block
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.bevel(offset=housing_geometry["more_geometry"]["bevel_radius"], segments=4)
        bpy.ops.object.mode_set(mode='OBJECT')

        # Apply boolean modifier to subtract inner block from outer block
        bpy.context.view_layer.objects.active = outer_block
        modifier = outer_block.modifiers.new(name="Boolean", type='BOOLEAN')
        modifier.object = inner_block
        modifier.operation = 'DIFFERENCE'
        bpy.ops.object.modifier_apply(modifier=modifier.name)

        # Remove inner block (we only needed it for the boolean operation)
        bpy.data.objects.remove(inner_block)
        
        # EXPORT HOUSING
        self.export_housing(jj)
        
        self.data["housing"]["housing_dimensions"]["outer_length"].append(housing_geometry["outer_length"])
        self.data["housing"]["housing_dimensions"]["outer_width"].append(housing_geometry["outer_width"])
        self.data["housing"]["housing_dimensions"]["outer_height"].append(housing_geometry["more_geometry"]["outer_height"])
        self.data["housing"]["housing_dimensions"]["inner_length"].append(inner_length)
        self.data["housing"]["housing_dimensions"]["inner_width"].append(inner_width)
        self.data["housing"]["housing_dimensions"]["inner_height"].append(inner_height)
        
        self.data["housing"]["housing_position"]["x"].append(x_loc)
        self.data["housing"]["housing_position"]["y"].append(y_loc)
        self.data["housing"]["housing_position"]["z"].append(z_loc)

        
    def export_housing(self, jj):
        if self.export_housing_bool == True: 
            #scale_factor=100
            
            if not os.path.exists(self.export_path):
                os.makedirs(self.export_path)
            
            bpy.ops.object.select_all(action='DESELECT')
            
            obj_name = f"housing_{jj}"
            obj = bpy.data.objects.get(obj_name)
            obj.select_set(True)
            
            bpy.context.view_layer.objects.active = obj
            
            '''
############Export Skalierung#####################################################################################################
            # Skaliere das Objekt
            bpy.ops.object.transform_apply(scale=True)  # Wende den Maßstab auf das Objekt an
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)  # Stelle sicher, dass alle Transformationen angewendet werden
            
            # Setze den Skalierungsfaktor
            bpy.context.active_object.scale *=scale_factor            
            '''
            
            ########## Decimate Modifier ####################################################

            # Add Decimate Modifier to reduce the number of vertices
            decimate_modifier = obj.modifiers.new(name="Decimate", type='DECIMATE')
            decimate_modifier.ratio = 0.1  # Adjust the ratio as needed (0.0 to 1.0)

            # Apply the Decimate Modifier
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier="Decimate")
            
            # Set export file path
            file_path = os.path.join(self.export_path, f"{jj+1}_{self.current_datetime}_housing.stl")
                
            # Export the combined object as .stl file
            # GANZ WICHTIG: Letzter Teil im Code: use_selection=True
            # QUELLE: https://docs.blender.org/api/current/bpy.ops.export_scene.html
            bpy.ops.export_mesh.stl(filepath=file_path, check_existing=False, filter_glob="*.stl", ascii=False, use_selection=True)        
            # Deselect all objects after export
            bpy.ops.object.select_all(action='DESELECT')
            print(f"[{self.current_datetime}] Export of housing_{jj+1} was successful, export path:\n{self.export_path}\n")
        else:
            print("No objects selected for export.")

    def cut_housing_zy(self, housing_geometry, jj):
        if self.cut_housing_zy_bool == True:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(self.housing_geometry["outer_length"]/2.0, 0, self.housing_geometry["more_geometry"]["outer_height"]/2.0))
            cut_block = bpy.context.active_object
            cut_block.scale = (housing_geometry["outer_length"], housing_geometry["outer_width"], housing_geometry["more_geometry"]["outer_height"])
            
            
            bpy.ops.object.select_all(action='DESELECT')
                    
            outer_block = bpy.data.objects.get(f"housing_{jj}")
            obj = bpy.data.objects.get(f"housing_{jj}")
            
            if outer_block:
                outer_block.select_set(True)
                bpy.context.view_layer.objects.active = outer_block

                # Apply boolean modifier to subtract cut_block from outer block
                modifier = outer_block.modifiers.new(name="Boolean", type='BOOLEAN')
                modifier.object = cut_block
                modifier.operation = 'DIFFERENCE'
                bpy.ops.object.modifier_apply(modifier=modifier.name)

                # Remove cut_block (we only needed it for the boolean operation)
                bpy.data.objects.remove(cut_block)
            else:
                print("outer_block not found!")

    def cut_housing_zx(self, housing_geometry, jj):
        if self.cut_housing_zx_bool == True:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(0, self.housing_geometry["outer_width"]/2.0, self.housing_geometry["more_geometry"]["outer_height"]/2.0))
            cut_block = bpy.context.active_object
            cut_block.scale = (housing_geometry["outer_length"], housing_geometry["outer_width"], housing_geometry["more_geometry"]["outer_height"])
            
            
            bpy.ops.object.select_all(action='DESELECT')
                    
            outer_block = bpy.data.objects.get(f"housing_{jj}")
            obj = bpy.data.objects.get(f"housing_{jj}")
            
            if outer_block:
                outer_block.select_set(True)
                bpy.context.view_layer.objects.active = outer_block

                # Apply boolean modifier to subtract cut_block from outer block
                modifier = outer_block.modifiers.new(name="Boolean", type='BOOLEAN')
                modifier.object = cut_block
                modifier.operation = 'DIFFERENCE'
                bpy.ops.object.modifier_apply(modifier=modifier.name)

                # Remove cut_block (we only needed it for the boolean operation)
                bpy.data.objects.remove(cut_block)
            else:
                print("outer_block not found!")

    def generate_cells(self):
        ######################################## GENERATING START ########################################
        for j in range(self.iterations):
            
            # SELECT AND DELETE ALL BEFORE CREATING NEW BATTERY
            if bpy.context.selected_objects:
                bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.select_by_type(type='MESH')
            bpy.ops.object.delete()
            self.delete_empty_objects()
            
            # CREATE NEW INNER BATTERY GEOMETRY
            self.create_and_export_inner_battery(j, self.anode,"anode")
            self.create_and_export_inner_battery(j, self.lower_anode_coating, "lower_anode_coating")
            self.create_and_export_inner_battery(j, self.upper_anode_coating, "upper_anode_coating")
            self.create_and_export_inner_battery(j, self.cathode,"cathode")
            self.create_and_export_inner_battery(j, self.lower_cathode_coating, "lower_cathode_coating")
            self.create_and_export_inner_battery(j, self.upper_cathode_coating, "upper_cathode_coating")
            
            # CREATE HOUSING
            self.create_and_export_housing(self.housing_geometry, j)
            
            filename = f"{j+1}_{self.current_datetime}_labeling.json"
            self.write_data_to_file(self.data, filename)
            
            # VISUALISATION OF INTERSECTIONS OF THE HOUSING
            self.cut_housing_zy(self.housing_geometry, j)
            self.cut_housing_zx(self.housing_geometry, j)
            
            print("Export done to: " + str(self.export_path))

        ######################################## GENERATING END ########################################

    def update_parameters_from_ui(self, params):
        # update time stamp for export
        self.current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.export_path = os.path.join(params["path"], self.export_folder)
        self.iterations = params["num_export"]
        
        self.seperator_height = params["separator"]
        self.anode_overhang_bool = params["overhang"]
        self.export_inner_battery_bool = True
        self.export_housing_bool = params["case"]
        self.cut_housing_zy_bool = params["cut_zy"]
        self.cut_housing_zx_bool = params["cut_zx"]
        self.bending_bool = params["bending"]
        
        self.max_angle = params["max_angle"]
        self.min_angle = params["min_angle"]

        self.x_variation = params["dev_x"]
        self.y_variation = params["dev_y"]
        
        self.anode = {
            "length": params["size_x"], # 0.1015
            "width": params["size_y"], # 0.050
            "height": params["size_z"], # 0.001
            "length_tol": 0.000,
            "max_overhang": params["max_overhang"], # 0.0068
            "min_overhang": params["min_overhang"], # 0.0023
            "width_tol": 0.000,
            "height_tol": 0.000,
            "amount": params["num_anodes"], # integer
            "color": (1, 0, 0, 1),  # red color (RGB values)
        }

        self.lower_anode_coating = {
            "length": params["size_x"],
            "width": params["size_y"],
            "height": params["size_z"],
            "length_tol": 0.000,
            "max_overhang": self.anode["max_overhang"],
            "min_overhang": self.anode["min_overhang"],
            "width_tol": 0.000,
            "height_tol": 0.000,
            "amount": self.anode["amount"],
            "color": (0, 0, 0, 1),  # black color (RGB values)
        }

        self.upper_anode_coating = {
            "length": params["size_x"],
            "width": params["size_y"],
            "height": params["size_z"],
            "length_tol": 0.000,
            "max_overhang": self.anode["max_overhang"],
            "min_overhang": self.anode["min_overhang"],
            "width_tol": 0.000,
            "height_tol": 0.000,
            "amount": self.anode["amount"],
            "color": (0, 0, 0, 1),  # black color (RGB values)
        }

        self.cathode = {
            "length": params["size_x"],
            "width": params["size_y"],
            "height": params["size_z"],
            "length_tol": 0.000,
            "width_tol": 0.000,
            "height_tol": 0.000,
            "amount": self.anode["amount"]-1, # integer
            "color": (0, 1, 0, 1),  # green color (RGB values)
        }

        self.lower_cathode_coating = {
            "length": params["size_x"],
            "width": params["size_y"],
            "height": params["size_z"],
            "length_tol": 0.000,
            "width_tol": 0.000,
            "height_tol": 0.000,
            "amount": self.anode["amount"]-1,
            "color": (0, 0, 1, 1),  # blue color (RGB values)
        }

        self.upper_cathode_coating = {
            "length": params["size_x"],
            "width": params["size_y"],
            "height": params["size_z"],
            "length_tol": 0.000,
            "width_tol": 0.000,
            "height_tol": 0.000,
            "amount": self.anode["amount"]-1,
            "color": (0, 0, 1, 1),  # blue color (RGB values)
        }

        # END VARIABLE PARAMETERSET

        self.housing_geometry = {
            # battery sizes
            "outer_width": (self.anode["width"] + self.y_variation*2 + 0.008), 
            "outer_length": (self.anode["length"] + self.anode["max_overhang"] + self.x_variation*2 + 0.008),  
            "wall_thickness": 0.001
        }

        self.anode["overhang"] = {
         # GIBT EINE ZUFÄLLIGE GLEITKOMMAZAHL IN DIESEM BEREICH ZURÜCK
         "anode_overhang": np.random.uniform(self.anode["min_overhang"], self.anode["max_overhang"])
        }

        # Formula for parametric positioning
        self.anode["position"] = {
            "z_position": ((self.anode["height"]/2.0) + (self.lower_anode_coating["height"])+self.seperator_height + (self.housing_geometry["wall_thickness"]/2.0)),
            "z_distance": self.anode["height"]+self.cathode["height"]+2*self.seperator_height+self.upper_anode_coating["height"]+self.lower_anode_coating["height"]+self.upper_cathode_coating["height"]+self.lower_cathode_coating["height"]
        }

        self.lower_anode_coating["position"] = {
            "z_position": self.anode["position"]["z_position"]-((self.anode["height"] + self.lower_anode_coating["height"]) / 2.0),
            "z_distance": self.anode["position"]["z_distance"]
        }

        self.upper_anode_coating["position"] = {
            "z_position": self.anode["position"]["z_position"]+((self.anode["height"] + self.upper_anode_coating["height"]) / 2.0),
            "z_distance": self.anode["position"]["z_distance"]
        }

        self.cathode["position"] = {
            "z_position": self.anode["position"]["z_position"]+(((self.anode["height"]+self.cathode["height"])/2)+self.upper_anode_coating["height"]+self.lower_cathode_coating["height"]+self.seperator_height),
            "z_distance": self.anode["height"]+self.cathode["height"]+2*self.seperator_height+self.upper_anode_coating["height"]+self.lower_anode_coating["height"]+self.upper_cathode_coating["height"]+self.lower_cathode_coating["height"]
        }

        self.lower_cathode_coating["position"] = {
            "z_position": (self.cathode["position"]["z_position"]-((self.cathode["height"]+self.lower_cathode_coating["height"])/2.0)),
            "z_distance": self.cathode["position"]["z_distance"]
        }

        self.upper_cathode_coating["position"] = {
            "z_position": (self.cathode["position"]["z_position"]+((self.cathode["height"]+self.lower_cathode_coating["height"])/2.0)),
            "z_distance": self.cathode["position"]["z_distance"]
        }

        self.housing_geometry["more_geometry"] = {
            "bevel_radius": 0.01,
            "outer_height": (self.anode["amount"]*self.anode["height"]) + (self.cathode["amount"]*self.cathode["height"]) + (self.lower_anode_coating["amount"]*self.lower_anode_coating["height"]) + (self.upper_anode_coating["amount"]*self.upper_anode_coating["height"]) + (self.lower_cathode_coating["amount"]*self.lower_cathode_coating["height"]) + (self.upper_cathode_coating["amount"]*self.upper_cathode_coating["height"]) + (2*self.anode["amount"]*self.seperator_height)+(self.housing_geometry["wall_thickness"]), 
        }

# ------------------------------------------------------------------------
#    Scene Properties UI
# ------------------------------------------------------------------------

class PathProperty(bpy.types.PropertyGroup):

    path: bpy.props.StringProperty(
        name="",
        description="Path to Directory",
        default="",
        maxlen=1024,
        subtype='DIR_PATH')

class FileProperty(bpy.types.PropertyGroup):

    file: bpy.props.StringProperty(
        name="",
        description="Path to File",
        default="",
        maxlen=1024,
        subtype='FILE_PATH')

bpy.types.Scene.checkbox_1 = bpy.props.BoolProperty(
    name="",
    description="",
    default = True)

bpy.types.Scene.checkbox_2 = bpy.props.BoolProperty(
    name="",
    description="",
    default = True) 

bpy.types.Scene.checkbox_3 = bpy.props.BoolProperty(
    name="",
    description="",
    default = True) 

bpy.types.Scene.checkbox_4 = bpy.props.BoolProperty(
    name="",
    description="",
    default = True) 

bpy.types.Scene.checkbox_5 = bpy.props.BoolProperty(
    name="",
    description="",
    default = True) 
 
# Number of Exports
bpy.types.Scene.num_slider = bpy.props.IntProperty(
    name="Number of Exported Variants",
    description="Adjust the value using this slider",
    default=1,  # Default value
    min=1,      # Minimum value
    max=1000       # Maximum value
)
       
# Number of Anodes
bpy.types.Scene.anode_slider = bpy.props.IntProperty(
    name="Number of Anodes",
    description="Adjust the value using this slider",
    default=10,  # Default value
    min=2,      # Minimum value
    max=100       # Maximum value
)

# Define a custom property to store the value
bpy.types.Scene.x_slider = bpy.props.FloatProperty(
    name="Size X",
    description="Adjust the value using this slider",
    default=0.1015,  # Default value
    min=0.0,      # Minimum value
    max=50       # Maximum value
)

# Define a custom property to store the value
bpy.types.Scene.y_slider = bpy.props.FloatProperty(
    name="Size Y",
    description="Adjust the value using this slider",
    default=0.050,  # Default value
    min=0.0,      # Minimum value
    max=50       # Maximum value
)

# Define a custom property to store the value
bpy.types.Scene.z_slider = bpy.props.FloatProperty(
    name="Size Z",
    description="Adjust the value using this slider",
    default=0.001,  # Default value
    min=0.0,      # Minimum value
    max=50       # Maximum value
)

# Define a custom property to store the value
bpy.types.Scene.separator_slider = bpy.props.FloatProperty(
    name="Size Separator",
    description="Adjust the value using this slider",
    default=0.001,  # Default value
    min=0.0,      # Minimum value
    max=50       # Maximum value
)

# Define a custom property to store the value
bpy.types.Scene.deviation_x_slider = bpy.props.FloatProperty(
    name="Deviation X",
    description="Adjust the value using this slider",
    default=0.001,  # Default value
    min=0.0,      # Minimum value
    max=0.1       # Maximum value
)

# Define a custom property to store the value
bpy.types.Scene.deviation_y_slider = bpy.props.FloatProperty(
    name="Deviation Y",
    description="Adjust the value using this slider",
    default=0.001,  # Default value
    min=0.0,      # Minimum value
    max=0.1      # Maximum value
)

# Define a custom property to store the value
bpy.types.Scene.max_overhang_slider = bpy.props.FloatProperty(
    name="Overhang Max",
    description="Adjust the value using this slider",
    default=0.0068,  # Default value
    min=0.0,      # Minimum value
    max=0.25       # Maximum value
)

# Define a custom property to store the value
bpy.types.Scene.min_overhang_slider = bpy.props.FloatProperty(
    name="Overhang Min",
    description="Adjust the value using this slider",
    default=0.0023,  # Default value
    min=0.0,      # Minimum value
    max=0.25      # Maximum value
)

# Define a custom property to store the value
bpy.types.Scene.max_angle_slider = bpy.props.FloatProperty(
    name="Bending Angle Max",
    description="Adjust the value using this slider",
    default=15.0,  # Default value
    min=0.0,      # Minimum value
    max=45.0      # Maximum value
)

# Define a custom property to store the value
bpy.types.Scene.min_angle_slider = bpy.props.FloatProperty(
    name="Bending Angle Min",
    description="Adjust the value using this slider",
    default=-15.0,  # Default value
    min=-45.0,      # Minimum value
    max=0      # Maximum value
)

# ------------------------------------------------------------------------
#    Classes
# ------------------------------------------------------------------------

# Messagebox Function
def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):
        def draw(self, context):
            self.layout.label(text=message)
        bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

# Define the panel class
class CustomPanel(bpy.types.Panel):
    bl_label = "BatteryCT Configuration"
    bl_idname = "PT_CustomPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BatteryCT'
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Add path tool
        layout.label(text="Load Config File:")        
        col = layout.column(align=True)
        col.prop(scene.path_tool_1, "file", text="")
        layout.operator("object.load_config_button")
        layout.operator("object.save_config_button")
        
        # Add path tool  
        layout.label(text="Output Folder Location:")       
        col = layout.column(align=True)
        col.prop(scene.path_tool_2, "path", text="")
        layout.prop(scene, "num_slider")
        layout.operator("object.export_button")
        
        layout.separator()
        layout.label(text="MODELLING SETTINGS:")  
        
        layout.prop(scene, "checkbox_1", text="Anode/Cathode Overhang?")
        layout.prop(scene, "checkbox_2", text="Export Battery Case?")
        layout.prop(scene, "checkbox_3", text="Cut Battery Case ZY?")
        layout.prop(scene, "checkbox_4", text="Cut Battery Case ZX?")
        layout.prop(scene, "checkbox_5", text="Anode/Cathode Bending?")
        
        # Add a slider to adjust the custom property value
        layout.prop(scene, "anode_slider")
        layout.label(text="Bending Angle Range:")
        layout.prop(scene, "max_angle_slider")
        layout.prop(scene, "min_angle_slider")
        layout.label(text="Ideal Size Anode/Cathode/Separator:")
        layout.prop(scene, "x_slider")
        layout.prop(scene, "y_slider")
        layout.prop(scene, "z_slider")
        layout.prop(scene, "separator_slider")
        
        layout.label(text="Max deviation from ideal size:")
        layout.prop(scene, "deviation_x_slider")
        layout.prop(scene, "deviation_y_slider")
        
        layout.label(text="Anode Overhang:")
        layout.prop(scene, "min_overhang_slider")
        layout.prop(scene, "max_overhang_slider")
        
        
        # Debug
        layout.separator()
        layout.label(text="Debugging:")
        layout.operator("object.data_button")
        


class DataButton(bpy.types.Operator):
    """Print All Data to console"""
    bl_idname = "object.data_button"
    bl_label = "Print Data"

    def execute(self, context):
        print("------------BatteryCT Parameters----------")
        print("Size-X: " + str(bpy.context.scene.x_slider))
        print("Size-Y: " + str(bpy.context.scene.y_slider))
        print("Size-Z: " + str(bpy.context.scene.z_slider))
        print("")
        print("NumAnodes: " + str(bpy.context.scene.anode_slider))
        # print the path to the console
        print("Config File Path: " + str(context.scene.path_tool_1.file))
        print("Output Folder Path: " + str(context.scene.path_tool_2.path))
        return {'FINISHED'}

class LoadConfig(bpy.types.Operator):
    bl_idname = "object.load_config_button"
    bl_label = "Load Config"

    def execute(self, context):
        #Shows a message box with a message, custom title, and a specific icon
        
        outpath = os.path.normpath(str(context.scene.path_tool_1.file))
        
        # Opening JSON file
        with open(outpath, 'r') as openfile:
            # Reading from json file
            json_object = json.load(openfile)
            
                
        context.scene.path_tool_2.path = json_object["path"]
        bpy.context.scene.num_slider = json_object["num_export"]
        bpy.context.scene.checkbox_1 = json_object["overhang"]
        bpy.context.scene.checkbox_2 = json_object["case"]
        bpy.context.scene.checkbox_3 = json_object["cut_zy"]
        bpy.context.scene.checkbox_4 = json_object["cut_zx"]
        bpy.context.scene.checkbox_5 = json_object["bending"]
        bpy.context.scene.deviation_x_slider = json_object["dev_x"]
        bpy.context.scene.deviation_y_slider = json_object["dev_y"]
        bpy.context.scene.anode_slider = json_object["num_anodes"]
        bpy.context.scene.x_slider = json_object["size_x"]
        bpy.context.scene.y_slider = json_object["size_y"]
        bpy.context.scene.z_slider = json_object["size_z"]
        bpy.context.scene.min_overhang_slider = json_object["min_overhang"]
        bpy.context.scene.max_overhang_slider = json_object["max_overhang"]
        bpy.context.scene.separator_slider = json_object["separator"]
        bpy.context.scene.max_angle_slider = json_object["max_angle"]
        bpy.context.scene.min_angle_slider = json_object["min_angle"]
        
        #Shows a message box with a message, custom title, and a specific icon
        ShowMessageBox("Configuration imported successfully", "Config Import", 'ERROR')
        
        return {'FINISHED'}

class SaveConfig(bpy.types.Operator):
    bl_idname = "object.save_config_button"
    bl_label = "Save Config"

    def execute(self, context):
        #Shows a message box with a message, custom title, and a specific icon
        
        outpath = os.path.normpath(str(context.scene.path_tool_1.file))
        
        params = {
            "path": str(context.scene.path_tool_2.path),
            "num_export": int(bpy.context.scene.num_slider),
            "overhang": bpy.context.scene.checkbox_1,
            "case": bpy.context.scene.checkbox_2,
            "cut_zy": bpy.context.scene.checkbox_3,
            "cut_zx": bpy.context.scene.checkbox_4,
            "bending": bpy.context.scene.checkbox_5,
            "dev_x": float(bpy.context.scene.deviation_x_slider),
            "dev_y": float(bpy.context.scene.deviation_y_slider),
            "num_anodes": int(bpy.context.scene.anode_slider),
            "size_x": float(bpy.context.scene.x_slider),
            "size_y": float(bpy.context.scene.y_slider),
            "size_z": float(bpy.context.scene.z_slider),
            "min_overhang": float(bpy.context.scene.min_overhang_slider),
            "max_overhang": float(bpy.context.scene.max_overhang_slider),
            "separator": float(bpy.context.scene.separator_slider),
            "max_angle": float(bpy.context.scene.max_angle_slider), 
            "min_angle": float(bpy.context.scene.min_angle_slider),  
        }
        
        json_object = json.dumps(params, indent=4)
        
        with open(outpath, "w") as outfile:
            outfile.write(json_object)
        
        #Shows a message box with a message, custom title, and a specific icon
        ShowMessageBox("Configuration exported successfully", "Config Export", 'ERROR')
        
        return {'FINISHED'}    

class Export(bpy.types.Operator):
    bl_idname = "object.export_button"
    bl_label = "Generate and Export Cell(s)"

    def execute(self, context):
        
        params = {
            "path": str(context.scene.path_tool_2.path),
            "num_export": int(bpy.context.scene.num_slider),
            "overhang": bpy.context.scene.checkbox_1,
            "case": bpy.context.scene.checkbox_2,
            "cut_zy": bpy.context.scene.checkbox_3,
            "cut_zx": bpy.context.scene.checkbox_4,
            "bending": bpy.context.scene.checkbox_5,
            "dev_x": float(bpy.context.scene.deviation_x_slider),
            "dev_y": float(bpy.context.scene.deviation_y_slider),
            "num_anodes": int(bpy.context.scene.anode_slider),
            "size_x": float(bpy.context.scene.x_slider),
            "size_y": float(bpy.context.scene.y_slider),
            "size_z": float(bpy.context.scene.z_slider),
            "min_overhang": float(bpy.context.scene.min_overhang_slider),
            "max_overhang": float(bpy.context.scene.max_overhang_slider),
            "separator": float(bpy.context.scene.separator_slider),
            "max_angle": float(bpy.context.scene.max_angle_slider), 
            "min_angle": float(bpy.context.scene.min_angle_slider),
           
        }
        
        modeler = Modeling()
        # Update parameters based on UI config
        modeler.update_parameters_from_ui(params)
        # Generate and export cells
        modeler.generate_cells()
        
        #Shows a message box with a message, custom title, and a specific icon
        ShowMessageBox("Cells generated successfully", "Cell Generation", 'ERROR')
        
        
        return {'FINISHED'}   
    

# ------------------------------------------------------------------------
#     Registration
# ------------------------------------------------------------------------

classes = (
    CustomPanel,
    DataButton,
    PathProperty,
    FileProperty,
    LoadConfig,
    SaveConfig,
    Export
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.path_tool_1 = bpy.props.PointerProperty(type=FileProperty)
    bpy.types.Scene.path_tool_2 = bpy.props.PointerProperty(type=PathProperty)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.path_tool_1
    del bpy.types.Scene.path_tool_1


if __name__ == "__main__":
    register()