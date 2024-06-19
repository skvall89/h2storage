# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 13:11:28 2024

@author: svallin
"""

#############################
# HYDROGEN STORAGE 2D-Model
#############################
import mph
import math
import numpy as np
################################
#MODELS 
################################

################################
# MODEL PARAMETERS
################################
#################################
#GEOMETRY PARAMETERS
#################################
model_width = 100 # meters
model_height = 250 # meters
storage_diameter = 35 # meters 
storage_height = 55 # meters
storage_depth = -100 # meters depth of storage roof
arc_length = 15 # arc length in y-axis meters

#################################
#ROCK PROPERTIES
#################################
k_rock = 2.96 # W/(m*K)
rho_rock = 2500 # kg/m^3
cp_rock = 725 # J/(kg*K)

#########################################################################################################
#MECHANICAL PROPERTIES - Hoek - Brown -criterion for unaltered jointed rock masses with hard intact rock !! sigma1 = sigma3 + sigma_ci*sqrt((m*sigma3)/(sigma_ci +S))
#########################################################################################################
compressive_strength = 200 # MPa sigma_ci = uniaxial compressive strength
youngs_modulus = 60 # GPa
poissons_ratio = 0.25
GSI = 75 #
D_hoek = 0.1 # 0 Undistrbed in-situ rock mass... - 1 very disturbed rock mass
m_i = 32 #Granite from Hoek and Marinos 2000. Constant values for intact rock from table.
m_hoek = m_i*math.exp((GSI-100)/(28*14*D_hoek))
s_hoek = math.exp((GSI-100)/(9-3*D_hoek))

#########################################################################################################
#MECHANICAL PROPERTIES Rock mass - Mohr-Colomb -criterion !! 
#########################################################################################################
cohesion = 1 # MPa 
friction_angle = 35 # degree

#########################################################################################################
#MECHANICAL PROPERTIES Lining boundary layer
#########################################################################################################
youngs_modulus_lining = 25 # GPa
rho_lining = 2300 # kg/m3
poissons_ratio_lining = 0.2
lining_thickness = 20 #cm
internal_pressure = 50 # bar

##############################################
#Mesh
##############################################
number_of_elements = 25 #number of elements at storage edge
max_element_size = 20 # m
max_element_growth_rate = 1.1 #maximum growth rate of elements

def create_h2storagemodel(criterion, model_dimension) :#h2_params, model
    client = mph.start(cores=4)
    pymodel = client.create('hydrogen_storage_model')
    h2storage = pymodel.java
    h2storage.component().create("comp1", True)
    if model_dimension == "2d":
        h2storage.component("comp1").geom().create("geom1", 2)
    elif model_dimension == "3d":
        h2storage.component("comp1").geom().create("geom1", 3)
        
    h2storage.component("comp1").mesh().create("mesh1")
    
    print("Setting up parameters...", end=" ")
    
    h2storage.param().group().create("par1")
    ##Set up model geometry parameters and internal pressure of hydrogen storage
    h2storage.param("par1").label("Model_geometry_parameters")
    h2storage.param("par1").set("W_model", f"{model_width}"+"[m]")
    h2storage.param("par1").set("H_model", f"{model_height}"+"[m]")
    h2storage.param("par1").set("storage_diameter", f"{storage_diameter}"+"[m]")
    h2storage.param("par1").set("storage_radius", f"({storage_diameter}/2)"+"[m]")
    h2storage.param("par1").set("storage_height", f"{storage_height}"+"[m]")
    h2storage.param("par1").set("storage_depth", f"{storage_depth}"+"[m]")
    h2storage.param("par1").set("arc_length", f"{arc_length}"+"[m]")
    h2storage.param("par1").set("int_pressure", f"{internal_pressure}"+"[bar]")
    h2storage.param("par1").descr("int_pressure", "Storage internal pressure due to pressurization")
    
    ##Set up model mechanical parameters for rock mass
    if criterion == "hoek-brown":
        h2storage.param().group().create("par2")
        h2storage.param("par2").label("Rock mass Hoek-Brown_criterion_parameters")
        h2storage.param("par2").set("rho_rock", f"{rho_rock}"+"[kg/m^3]")
        h2storage.param("par2").descr("rho_rock", "Density of rock")
        h2storage.param("par2").set("sigma_ci", f"{compressive_strength}"+"[MPa]")
        h2storage.param("par2").descr("sigma_ci", "Uniaxial compressive strength UCS")
        h2storage.param("par2").set("E_rock", f"{youngs_modulus}"+"[GPa]")
        h2storage.param("par2").descr("E_rock", "Young's Modulus of rock")
        h2storage.param("par2").set("v_rock", f"{poissons_ratio}")
        h2storage.param("par2").descr("v_rock", "Poisson's ratio of rock")
        h2storage.param("par2").set("GSI", f"{GSI}")
        h2storage.param("par2").descr("GSI", "Geological Strength Index")
        h2storage.param("par2").set("GSI", f"{GSI}")
        h2storage.param("par2").descr("GSI", "Geological Strength Index")
        h2storage.param("par2").set("D_hoek", f"{D_hoek}")
        h2storage.param("par2").descr("D_hoek", "Disturbance factor")
        h2storage.param("par2").set("m_i", f"{m_i}")
        h2storage.param("par2").descr("m_i", "Intact rock constant")
        h2storage.param("par2").set("m_hoek", f"{m_hoek}")
        h2storage.param("par2").descr("m_hoek", "Reduced value of intact rock constant")
        h2storage.param("par2").set("s_hoek", f"{s_hoek}")

    elif criterion == "mohr-coulomb":
        h2storage.param().group().create("par2")
        h2storage.param("par2").label("Rock mass Mohr-Coulomb_criterion_parameters")
        h2storage.param("par2").set("rho_rock", f"{rho_rock}"+"[kg/m^3]")
        h2storage.param("par2").set("E_rock", f"{youngs_modulus}"+"[GPa]")
        h2storage.param("par2").descr("E_rock", "Young's Modulus of rock")
        h2storage.param("par2").set("v_rock", f"{poissons_ratio}")
        h2storage.param("par2").descr("v_rock", "Poisson's ratio of rock")
        h2storage.param("par2").set("c_rock", f"{cohesion}"+"[MPa]")
        h2storage.param("par2").descr("c_rock", "cohesion of rock")
        h2storage.param("par2").set("phi_rock", f"{friction_angle}"+"[deg]")
        h2storage.param("par2").descr("phi_rock", "friction angle of rock")
        
    ##Set up model mechanical parameters for lining
    h2storage.param().group().create("par3")
    h2storage.param("par3").label("Lining mechanical parameters")
    h2storage.param("par3").set("rho_lining", f"{rho_lining}"+"[kg/m^3]")
    h2storage.param("par3").descr("rho_lining", "Density of lining")
    h2storage.param("par3").set("E_lining", f"{youngs_modulus_lining}"+"[GPa]")
    h2storage.param("par3").descr("E_lining", "Young's Modulus lining")
    h2storage.param("par3").set("v_lining", f"{poissons_ratio_lining}")
    h2storage.param("par3").descr("v_lining", "Poisson's ratio lining")
    h2storage.param("par3").set("l_thickness", f"{lining_thickness}"+"[cm]")
    ## Mesh parameters
    h2storage.param().group().create("par4")
    h2storage.param("par4").label("Mesh_parameters")
    h2storage.param("par4").set("num_elem", f"{number_of_elements}")
    h2storage.param("par4").descr("num_elem", "Numer of elements at storage boundary multiplied by 3")
    h2storage.param("par4").set("max_elem", f"{max_element_size}")
    h2storage.param("par4").descr("num_elem", "Maximum element size in the rock mass")
    h2storage.param("par4").set("max_growth", f"{max_element_growth_rate}")
    h2storage.param("par4").descr("max_growth", "Maximum element growth rate in the rock mass")
    print("Done")
    
    ##################################################################################
    #Set up geometry and selections
    ##################################################################################
    print("Creating geometry...", end=" ")
    
    ##Geometry if model 2-dimensional#############
    if model_dimension == "2d":
        h2storage.component("comp1").geom("geom1").create("r1", "Rectangle") # set up rock mass geometry
        h2storage.component("comp1").geom("geom1").feature("r1").label("Rock_mass")
        h2storage.component("comp1").geom("geom1").create("r2", "Rectangle") # set up storage geometry
        h2storage.component("comp1").geom("geom1").feature("r2").label("Storage")
        h2storage.component("comp1").geom("geom1").feature("r1").set("size", ("W_model", "H_model")) # set up rock mass dimensions
        h2storage.component("comp1").geom("geom1").feature("r1").set("pos", ("0", "-H_model")) # set up rock mass position. 0-point surface 
        h2storage.component("comp1").geom("geom1").feature("r2").set("size", ("storage_radius", "storage_height")) # set up storage dimensions
        h2storage.component("comp1").geom("geom1").feature("r2").set("pos", ("0", "storage_depth-storage_height")) # set up rock mass position. Depth of storage is the top part the storage
        h2storage.component("comp1").geom("geom1").create("qb1", "QuadraticBezier") # set up arc in the top of the storage
        h2storage.component("comp1").geom("geom1").feature("qb1").label("Top_arc - quadratic b\u00e9zier")
        h2storage.component("comp1").geom("geom1").feature("qb1").setIndex("p", "0", 0, 0)
        h2storage.component("comp1").geom("geom1").feature("qb1").setIndex("p", "storage_radius", 0, 1)
        h2storage.component("comp1").geom("geom1").feature("qb1").setIndex("p", "storage_radius", 0, 2)
        h2storage.component("comp1").geom("geom1").feature("qb1").setIndex("p", "storage_depth", 1, 0)
        h2storage.component("comp1").geom("geom1").feature("qb1").setIndex("p", "storage_depth", 1, 1)
        h2storage.component("comp1").geom("geom1").feature("qb1").setIndex("p", "storage_depth-arc_length", 1, 2)        
        h2storage.component("comp1").geom("geom1").create("qb2", "QuadraticBezier") # set up arc in the bottom of the storage
        h2storage.component("comp1").geom("geom1").feature("qb2").label("Bottom_arc - quadratic b\u00e9zier")
        h2storage.component("comp1").geom("geom1").feature("qb2").setIndex("p", "0", 0, 0)
        h2storage.component("comp1").geom("geom1").feature("qb2").setIndex("p", "storage_radius", 0, 1)
        h2storage.component("comp1").geom("geom1").feature("qb2").setIndex("p", "storage_radius", 0, 2)
        h2storage.component("comp1").geom("geom1").feature("qb2").setIndex("p", "storage_depth-storage_height", 1, 0)
        h2storage.component("comp1").geom("geom1").feature("qb2").setIndex("p", "storage_depth-storage_height", 1, 1)
        h2storage.component("comp1").geom("geom1").feature("qb2").setIndex("p", "storage_depth-storage_height+arc_length", 1, 2)  
        h2storage.component("comp1").geom("geom1").create("csol1", "ConvertToSolid") # Convert_intersection_of_arcs_and_rectangle_to_domain
        h2storage.component("comp1").geom("geom1").feature("csol1").label("intersection_arcs_rectangle_to_domain")
        h2storage.component("comp1").geom("geom1").feature("csol1").selection("input").set("qb1", "qb2", "r2") #arcs + storage rectangle
    
    ##Geometry if model 3-dimensional#############
    elif model_dimension == "3d":
        h2storage.component("comp1").geom("geom1").create("blk1", "Block") # set up rock mass geometry
        h2storage.component("comp1").geom("geom1").feature("blk1").label("Rock_mass")
        h2storage.component("comp1").geom("geom1").feature("blk1").set("size", ("W_model", "W_model", "H_model"))
        h2storage.component("comp1").geom("geom1").feature("blk1").set("pos", ("0", "0", "-H_model"))
        h2storage.component("comp1").geom("geom1").create("wp1", "WorkPlane") # set up storage geometry
        h2storage.component("comp1").geom("geom1").feature("wp1").set("quickplane", "xz")
        h2storage.component("comp1").geom("geom1").feature("wp1").label("Work Plane for creating storage geom.")
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().create("r1", "Rectangle")
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature("r1").label("Storage")
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature("r1").set("size", ("storage_radius", "storage_height")) # set up storage dimensions
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature("r1").set("pos", ("0", "storage_depth-storage_height")) # set up rock mass position. Depth of storage is the top part the storage
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().create("qb1", "QuadraticBezier") # set up arc in the top of the storage
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature("qb1").label("Top_arc - quadratic b\u00e9zier")
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature("qb1").setIndex("p", "0", 0, 0)
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature("qb1").setIndex("p", "storage_radius", 0, 1)
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature("qb1").setIndex("p", "storage_radius", 0, 2)
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature("qb1").setIndex("p", "storage_depth", 1, 0)
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature("qb1").setIndex("p", "storage_depth", 1, 1)
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature("qb1").setIndex("p", "storage_depth-arc_length", 1, 2)      
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().create("qb2", "QuadraticBezier") # set up arc in the bottom of the storage
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature("qb2").label("Bottom_arc - quadratic b\u00e9zier")
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature("qb2").setIndex("p", "0", 0, 0)
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature("qb2").setIndex("p", "storage_radius", 0, 1)
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature("qb2").setIndex("p", "storage_radius", 0, 2)
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature("qb2").setIndex("p", "storage_depth-storage_height", 1, 0)
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature("qb2").setIndex("p", "storage_depth-storage_height", 1, 1)
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature("qb2").setIndex("p", "storage_depth-storage_height+arc_length", 1, 2)  
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().create("csol1", "ConvertToSolid") # Convert_intersection_of_arcs_and_rectangle_to_domain
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature("csol1").label("intersection_arcs_rectangle_to_domain")
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature("csol1").selection("input").set("qb1", "qb2", "r1") #arcs + storage rectangle

    ##################################################################################
    #Set up selections for creating storage geometry
    ##################################################################################
    bnd_2d = 1 #select boundary
    dmn_2d = 2 #select domain
    bnd_3d = 2
    dmn_3d = 3
    create_top_arc = "boxsel1"
    create_bottom_arc = "boxsel2"
    arc_sel = "csel1"
    ####Geometry if model 2-dimensional#############
    if model_dimension == "2d":
        h2storage.component("comp1").geom("geom1").selection().create("csel1", "CumulativeSelection")
        h2storage.component("comp1").geom("geom1").selection().create("csel2", "CumulativeSelection")
        h2storage.component("comp1").geom("geom1").selection().create("csel3", "CumulativeSelection")
        ##################################################################################
        h2storage.component("comp1").geom("geom1").create(create_top_arc, "BoxSelection")
        h2storage.component("comp1").geom("geom1").feature(create_top_arc).label("top_arc_selection")
        h2storage.component("comp1").geom("geom1").feature(create_top_arc).set("entitydim", f"{dmn_2d}")
        h2storage.component("comp1").geom("geom1").feature(create_top_arc).set("xmin", "storage_radius")
        h2storage.component("comp1").geom("geom1").feature(create_top_arc).set("xmax", "storage_radius")
        h2storage.component("comp1").geom("geom1").feature(create_top_arc).set("ymin", "storage_depth")
        h2storage.component("comp1").geom("geom1").feature(create_top_arc).set("ymax", "storage_depth")
        h2storage.component("comp1").geom("geom1").feature(create_top_arc).set("condition", "somevertex")
        h2storage.component("comp1").geom("geom1").feature(create_top_arc).set("contributeto", arc_sel)
        h2storage.component("comp1").geom("geom1").create(create_bottom_arc, "BoxSelection")
        h2storage.component("comp1").geom("geom1").feature(create_bottom_arc).label("bottom_arc_selection")
        h2storage.component("comp1").geom("geom1").feature(create_bottom_arc).set("entitydim", f"{dmn_2d}")
        h2storage.component("comp1").geom("geom1").feature(create_bottom_arc).set("xmin", "storage_radius")
        h2storage.component("comp1").geom("geom1").feature(create_bottom_arc).set("xmax", "storage_radius")
        h2storage.component("comp1").geom("geom1").feature(create_bottom_arc).set("ymin", "storage_depth-storage_height")
        h2storage.component("comp1").geom("geom1").feature(create_bottom_arc).set("ymax", "storage_depth-storage_height")
        h2storage.component("comp1").geom("geom1").feature(create_bottom_arc).set("condition", "somevertex")
        h2storage.component("comp1").geom("geom1").feature(create_bottom_arc).set("contributeto", arc_sel)
    
    ####Geometry if model 3-dimensional#############
    elif model_dimension == "3d":
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().selection().create(arc_sel , "CumulativeSelection")
        h2storage.component("comp1").geom("geom1").selection().create(arc_sel, "CumulativeSelection")
        h2storage.component("comp1").geom("geom1").selection(arc_sel).label("arc_sel") 
        
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().create(create_top_arc, "BoxSelection")
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature(create_top_arc).label("top_arc_selection")
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature(create_top_arc).set("entitydim", f"{dmn_2d}")
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature(create_top_arc).set("xmin", "storage_radius")
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature(create_top_arc).set("xmax", "storage_radius")
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature(create_top_arc).set("ymin", "storage_depth")
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature(create_top_arc).set("ymax", "storage_depth")
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature(create_top_arc).set("condition", "somevertex")
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature(create_top_arc).set("contributeto", arc_sel)
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().create(create_bottom_arc, "BoxSelection")
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature(create_bottom_arc).label("bottom_arc_selection")
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature(create_bottom_arc).set("entitydim", f"{dmn_2d}")
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature(create_bottom_arc).set("xmin", "storage_radius")
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature(create_bottom_arc).set("xmax", "storage_radius")
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature(create_bottom_arc).set("ymin", "storage_depth-storage_height")
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature(create_bottom_arc).set("ymax", "storage_depth-storage_height")
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature(create_bottom_arc).set("condition", "somevertex")
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature(create_bottom_arc).set("contributeto", arc_sel)
        
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().create("del1", "Delete") # delete rectangle edges for arc shape
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature("del1").selection("input").init(dmn_2d)
        h2storage.component("comp1").geom("geom1").feature("wp1").geom().feature("del1").selection("input").named(arc_sel)
    
    ###################################################
    # Set up selections for boundary conditions
    ###################################################
    ##2Dimensional
    symmetry_bnd = "boxsel3"
    faraway_bnd = "boxsel4"
    bottom_bnd_2d = "boxsel5"
    h2storage_sel_2d = "csel2"
    storage_outer_bnd_2d = "csel3"
    ##3Dimensional
    symmetry_bnd1 = "boxsel3"
    symmetry_bnd2 = "boxsel4"
    symmetry_bnd_sel = "csel2"
    faraway_bnd1 = "boxsel5"
    faraway_bnd2 = "boxsel6"
    faraway_bnd_sel = "csel3"
    bottom_bnd_3d = "boxsel7"
    h2storage_sel_3d = "csel4"
    storage_outer_bnd_3d = "csel5"
    
    if model_dimension == "2d":
        h2storage.component("comp1").geom("geom1").create(symmetry_bnd, "BoxSelection")
        h2storage.component("comp1").geom("geom1").feature(symmetry_bnd).label("symmetry_bnd_selection")
        h2storage.component("comp1").geom("geom1").feature(symmetry_bnd).set("entitydim", f"{bnd_2d}")
        h2storage.component("comp1").geom("geom1").feature(symmetry_bnd).set("xmin", "0")
        h2storage.component("comp1").geom("geom1").feature(symmetry_bnd).set("xmax", "0")
        h2storage.component("comp1").geom("geom1").feature(symmetry_bnd).set("ymin", "-H_model")
        h2storage.component("comp1").geom("geom1").feature(symmetry_bnd).set("ymax", "0")
        h2storage.component("comp1").geom("geom1").feature(symmetry_bnd).set("condition", "inside")
        h2storage.component("comp1").geom("geom1").create(faraway_bnd, "BoxSelection")
        h2storage.component("comp1").geom("geom1").feature(faraway_bnd).label("faraway_bnd_selection")
        h2storage.component("comp1").geom("geom1").feature(faraway_bnd).set("entitydim", f"{bnd_2d}")
        h2storage.component("comp1").geom("geom1").feature(faraway_bnd).set("xmin", "W_model")
        h2storage.component("comp1").geom("geom1").feature(faraway_bnd).set("xmax", "W_model")
        h2storage.component("comp1").geom("geom1").feature(faraway_bnd).set("ymin", "-H_model")
        h2storage.component("comp1").geom("geom1").feature(faraway_bnd).set("ymax", "0")
        h2storage.component("comp1").geom("geom1").feature(faraway_bnd).set("condition", "inside")
        h2storage.component("comp1").geom("geom1").create(bottom_bnd_2d, "BoxSelection")
        h2storage.component("comp1").geom("geom1").feature(bottom_bnd_2d).label("bottom_bnd_selection")
        h2storage.component("comp1").geom("geom1").feature(bottom_bnd_2d).set("entitydim", f"{bnd_2d}")
        h2storage.component("comp1").geom("geom1").feature(bottom_bnd_2d).set("xmin", "0")
        h2storage.component("comp1").geom("geom1").feature(bottom_bnd_2d).set("xmax", "W_model")
        h2storage.component("comp1").geom("geom1").feature(bottom_bnd_2d).set("ymin", "-H_model")
        h2storage.component("comp1").geom("geom1").feature(bottom_bnd_2d).set("ymax", "-H_model")
        h2storage.component("comp1").geom("geom1").feature(bottom_bnd_2d).set("condition", "inside")
        
        ##Delete rectangle edges around arc
        h2storage.component("comp1").geom("geom1").create("del1", "Delete") # delete rectangle edges for arc shape
        h2storage.component("comp1").geom("geom1").feature("del1").selection("input").init(dmn_2d)
        h2storage.component("comp1").geom("geom1").feature("del1").selection("input").named(arc_sel)
        h2storage.component("comp1").geom("geom1").feature("del1").set("contributeto", h2storage_sel_2d)
        h2storage.component("comp1").geom("geom1").selection(h2storage_sel_2d).label("h2storage_sel")
        h2storage.component("comp1").geom("geom1").feature("del1").set("selresult", "on")
        h2storage.component("comp1").geom("geom1").feature("del1").set("color", "10")

        h2storage.component("comp1").geom("geom1").create("difsel1", "DifferenceSelection")
        h2storage.component("comp1").geom("geom1").feature("difsel1").set("entitydim", f"{bnd_2d}")
        h2storage.component("comp1").geom("geom1").feature("difsel1").set("add", h2storage_sel_2d)
        h2storage.component("comp1").geom("geom1").feature("difsel1").set("subtract", symmetry_bnd)
        h2storage.component("comp1").geom("geom1").selection(storage_outer_bnd_2d).label("storage_outer_bnd")
        h2storage.component("comp1").geom("geom1").feature("difsel1").set("contributeto", storage_outer_bnd_2d)
        h2storage.component("comp1").geom("geom1").run()
    
    elif model_dimension == "3d":
        #################################################    
        ###set up 3D storage and selections for 3D model#
        #################################################
        
        h2storage.component("comp1").geom("geom1").selection().create(symmetry_bnd_sel, "CumulativeSelection")
        h2storage.component("comp1").geom("geom1").selection(symmetry_bnd_sel).label("symmetry_bnd_sel")
        h2storage.component("comp1").geom("geom1").selection().create(faraway_bnd_sel, "CumulativeSelection")
        h2storage.component("comp1").geom("geom1").selection(faraway_bnd_sel).label("faraway_bnd_sel")
        h2storage.component("comp1").geom("geom1").selection().create(h2storage_sel_3d, "CumulativeSelection")
        h2storage.component("comp1").geom("geom1").selection(h2storage_sel_3d).label("h2storage_sel")
        h2storage.component("comp1").geom("geom1").selection().create(storage_outer_bnd_3d, "CumulativeSelection")
        h2storage.component("comp1").geom("geom1").selection(storage_outer_bnd_3d).label("storage_outer_bnd")
        
        ##Create storage geometry 1/4 symmetry##########
        h2storage.component("comp1").geom("geom1").feature().create("rev1", "Revolve")
        h2storage.component("comp1").geom("geom1").feature("rev1").label("3D_storage [1/4]")
        h2storage.component("comp1").geom("geom1").feature("rev1").set("workplane", "wp1") ### Create 3d storage, symmetry 1/4
        h2storage.component("comp1").geom("geom1").feature("rev1").selection("input").set("wp1")
        h2storage.component("comp1").geom("geom1").feature("rev1").set("angtype", "specang")
        h2storage.component("comp1").geom("geom1").feature("rev1").set("angle2", "90")
        h2storage.component("comp1").geom("geom1").feature("rev1").set("selresult", "on")
        h2storage.component("comp1").geom("geom1").feature("rev1").set("contributeto", h2storage_sel_3d)
        
        h2storage.component("comp1").geom("geom1").create(symmetry_bnd1, "BoxSelection")
        h2storage.component("comp1").geom("geom1").feature(symmetry_bnd1).label("symmetry_bnd_selection_xaxis")
        h2storage.component("comp1").geom("geom1").feature(symmetry_bnd1).set("entitydim", f"{bnd_3d}")
        h2storage.component("comp1").geom("geom1").feature(symmetry_bnd1).set("xmin", "0")
        h2storage.component("comp1").geom("geom1").feature(symmetry_bnd1).set("xmax", "W_model")
        h2storage.component("comp1").geom("geom1").feature(symmetry_bnd1).set("ymin", "0")
        h2storage.component("comp1").geom("geom1").feature(symmetry_bnd1).set("ymax", "0")
        h2storage.component("comp1").geom("geom1").feature(symmetry_bnd1).set("zmin", "-H_model")
        h2storage.component("comp1").geom("geom1").feature(symmetry_bnd1).set("zmax", "0")
        h2storage.component("comp1").geom("geom1").feature(symmetry_bnd1).set("condition", "inside")
        h2storage.component("comp1").geom("geom1").feature(symmetry_bnd1).set("contributeto", symmetry_bnd_sel)
        
        h2storage.component("comp1").geom("geom1").create(symmetry_bnd2, "BoxSelection")
        h2storage.component("comp1").geom("geom1").feature(symmetry_bnd2).label("symmetry_bnd_selection_yaxis")
        h2storage.component("comp1").geom("geom1").feature(symmetry_bnd2).set("entitydim", f"{bnd_3d}")
        h2storage.component("comp1").geom("geom1").feature(symmetry_bnd2).set("xmin", "0")
        h2storage.component("comp1").geom("geom1").feature(symmetry_bnd2).set("xmax", "0")
        h2storage.component("comp1").geom("geom1").feature(symmetry_bnd2).set("ymin", "0")
        h2storage.component("comp1").geom("geom1").feature(symmetry_bnd2).set("ymax", "W_model")
        h2storage.component("comp1").geom("geom1").feature(symmetry_bnd2).set("zmin", "-H_model")
        h2storage.component("comp1").geom("geom1").feature(symmetry_bnd2).set("zmax", "0")
        h2storage.component("comp1").geom("geom1").feature(symmetry_bnd2).set("condition", "inside")
        h2storage.component("comp1").geom("geom1").feature(symmetry_bnd2).set("contributeto", symmetry_bnd_sel)
        
        h2storage.component("comp1").geom("geom1").create(faraway_bnd1, "BoxSelection")
        h2storage.component("comp1").geom("geom1").feature(faraway_bnd1).label("faraway_bnd_selection_xaxis")
        h2storage.component("comp1").geom("geom1").feature(faraway_bnd1).set("entitydim", f"{bnd_3d}")
        h2storage.component("comp1").geom("geom1").feature(faraway_bnd1).set("xmin", "0")
        h2storage.component("comp1").geom("geom1").feature(faraway_bnd1).set("xmax", "W_model")
        h2storage.component("comp1").geom("geom1").feature(faraway_bnd1).set("ymin", "W_model")
        h2storage.component("comp1").geom("geom1").feature(faraway_bnd1).set("ymax", "W_model")
        h2storage.component("comp1").geom("geom1").feature(faraway_bnd1).set("zmin", "-H_model")
        h2storage.component("comp1").geom("geom1").feature(faraway_bnd1).set("zmax", "0")
        h2storage.component("comp1").geom("geom1").feature(faraway_bnd1).set("condition", "inside")
        h2storage.component("comp1").geom("geom1").feature(faraway_bnd1).set("contributeto", faraway_bnd_sel)
        
        h2storage.component("comp1").geom("geom1").create(faraway_bnd2, "BoxSelection")
        h2storage.component("comp1").geom("geom1").feature(faraway_bnd2).label("faraway_bnd_selection_yaxis")
        h2storage.component("comp1").geom("geom1").feature(faraway_bnd2).set("entitydim", f"{bnd_3d}")
        h2storage.component("comp1").geom("geom1").feature(faraway_bnd2).set("xmin", "W_model")
        h2storage.component("comp1").geom("geom1").feature(faraway_bnd2).set("xmax", "W_model")
        h2storage.component("comp1").geom("geom1").feature(faraway_bnd2).set("ymin", "0")
        h2storage.component("comp1").geom("geom1").feature(faraway_bnd2).set("ymax", "W_model")
        h2storage.component("comp1").geom("geom1").feature(faraway_bnd2).set("zmin", "-H_model")
        h2storage.component("comp1").geom("geom1").feature(faraway_bnd2).set("zmax", "0")
        h2storage.component("comp1").geom("geom1").feature(faraway_bnd2).set("condition", "inside")
        h2storage.component("comp1").geom("geom1").feature(faraway_bnd2).set("contributeto", faraway_bnd_sel)
        
        h2storage.component("comp1").geom("geom1").create(bottom_bnd_3d, "BoxSelection")
        h2storage.component("comp1").geom("geom1").feature(bottom_bnd_3d).label("bottom_bnd_selection")
        h2storage.component("comp1").geom("geom1").feature(bottom_bnd_3d).set("entitydim", f"{bnd_3d}")
        h2storage.component("comp1").geom("geom1").feature(bottom_bnd_3d).set("xmin", "0")
        h2storage.component("comp1").geom("geom1").feature(bottom_bnd_3d).set("xmax", "W_model")
        h2storage.component("comp1").geom("geom1").feature(bottom_bnd_3d).set("ymin", "0")
        h2storage.component("comp1").geom("geom1").feature(bottom_bnd_3d).set("ymax", "W_model")
        h2storage.component("comp1").geom("geom1").feature(bottom_bnd_3d).set("zmin", "-H_model")
        h2storage.component("comp1").geom("geom1").feature(bottom_bnd_3d).set("zmax", "-H_model")
        h2storage.component("comp1").geom("geom1").feature(bottom_bnd_3d).set("condition", "inside")

        h2storage.component("comp1").geom("geom1").create("difsel1", "DifferenceSelection")
        h2storage.component("comp1").geom("geom1").feature("difsel1").set("entitydim", f"{bnd_3d}")
        h2storage.component("comp1").geom("geom1").feature("difsel1").set("add", h2storage_sel_3d)
        h2storage.component("comp1").geom("geom1").feature("difsel1").set("subtract", symmetry_bnd_sel)
        h2storage.component("comp1").geom("geom1").feature("difsel1").set("contributeto", storage_outer_bnd_3d)
        h2storage.component("comp1").geom("geom1").run()

    print("Done")
    ##################################################################################
    #Set up material properties
    ##################################################################################
    print("Creating material...", end=" ")
    ################################
    # Rock mass material properties
    ################################
    if criterion == "hoek-brown":
        h2storage.component("comp1").material().create("mat1", "Common")
        h2storage.component("comp1").material("mat1").label("Rock mass")
        h2storage.component("comp1").material("mat1").propertyGroup().create("Enu", "Young's_modulus_and_Poisson's_ratio")
        h2storage.component("comp1").material("mat1").propertyGroup().create("HoekBrown", "Hoek_Brown")
        h2storage.component("comp1").material("mat1").propertyGroup().create("YieldStressParameters", "Yield_stress_parameters")
        h2storage.component("comp1").material("mat1").propertyGroup("Enu").set("E", "E_rock")
        h2storage.component("comp1").material("mat1").propertyGroup("Enu").set("nu", "v_rock")
        h2storage.component("comp1").material("mat1").propertyGroup("def").set("density", "rho_rock")
        h2storage.component("comp1").material("mat1").propertyGroup("HoekBrown").set("sHB", "s_hoek")
        h2storage.component("comp1").material("mat1").propertyGroup("HoekBrown").set("mHB", "m_hoek")
        h2storage.component("comp1").material("mat1").propertyGroup("YieldStressParameters").set("sigmauc", "sigma_ci")
    elif criterion == "mohr-coulomb":
        h2storage.component("comp1").material().create("mat1", "Common")
        h2storage.component("comp1").material("mat1").label("Rock mass")
        h2storage.component("comp1").material("mat1").propertyGroup().create("Enu", "Young's_modulus_and_Poisson's_ratio")
        h2storage.component("comp1").material("mat1").propertyGroup().create("MohrCoulomb", "Mohr_Coulomb_criterion")
        h2storage.component("comp1").material("mat1").propertyGroup("Enu").set("E", "E_rock")
        h2storage.component("comp1").material("mat1").propertyGroup("Enu").set("nu", "v_rock")
        h2storage.component("comp1").material("mat1").propertyGroup("def").set("density", "rho_rock")
        h2storage.component("comp1").material("mat1").propertyGroup("MohrCoulomb").set("cohesion", "c_rock")
        h2storage.component("comp1").material("mat1").propertyGroup("MohrCoulomb").set("internalphi", "phi_rock")
    ##############################
    #Lining material properties
    ##############################
    h2storage.component("comp1").material().create("mat2", "Common")
    h2storage.component("comp1").material("mat2").label("Lining")
    h2storage.component("comp1").material("mat2").set("family", "concrete")
    if model_dimension == "2d":
        h2storage.component("comp1").material("mat2").selection().geom("geom1", bnd_2d)
        h2storage.component("comp1").material("mat2").selection().named(f"geom1_{storage_outer_bnd_2d}_bnd")
    elif model_dimension == "3d":
        h2storage.component("comp1").material("mat2").selection().geom("geom1", bnd_3d)
        h2storage.component("comp1").material("mat2").selection().named(f"geom1_{storage_outer_bnd_3d}_bnd")
    h2storage.component("comp1").material("mat2").propertyGroup().create("Enu", "Young's_modulus_and_Poisson's_ratio")
    h2storage.component("comp1").material("mat2").propertyGroup("Enu").set("E", "E_lining")
    h2storage.component("comp1").material("mat2").propertyGroup("Enu").set("nu", "v_lining")
    h2storage.component("comp1").material("mat2").propertyGroup("def").set("density", "rho_lining")
    print("Done")
    
    ##################################################################################
    #Set up physics
    ##################################################################################
    print("Setting up physics solid mechanics...", end=" ")
    h2storage.component("comp1").physics().create("solid", "SolidMechanics", "geom1") # Set up solid mechanics physics
    if model_dimension == "2d":
        if criterion == "hoek-brown":
            h2storage.component("comp1").physics("solid").feature("lemm1").create("rock1", "Rocks", dmn_2d) #Rock mass Hoek-Brown criteria    
            h2storage.component("comp1").physics("solid").feature("lemm1").feature("rock1").label("Rock mass - Hoek-Brown")
        elif criterion == "mohr-coulomb":
            h2storage.component("comp1").physics("solid").feature("lemm1").create("soil1", "SoilModel", dmn_2d)
            h2storage.component("comp1").physics("solid").feature("lemm1").feature("soil1").set("YieldCriterion", "MohrCoulomb")
            h2storage.component("comp1").physics("solid").feature("lemm1").feature("soil1").label("Rock mass - Mohr-Coulomb")
        h2storage.component("comp1").physics("solid").feature("lemm1").create("iss1", "InitialStressandStrain", dmn_2d)
        h2storage.component("comp1").physics("solid").feature("lemm1").create("act1", "Activation", dmn_2d)
        h2storage.component("comp1").physics("solid").create("roll1", "Roller", bnd_2d)  # Boundary condition for outer edge - no displacement in x-directio
        h2storage.component("comp1").physics("solid").feature("lemm1").feature("act1").selection().named(f"geom1_{h2storage_sel_2d}_dom")
        h2storage.component("comp1").physics("solid").feature("roll1").selection().named(f"geom1_{faraway_bnd}")
        h2storage.component("comp1").physics("solid").feature("fix1").selection().named(f"geom1_{bottom_bnd_2d}")
        h2storage.component("comp1").physics("solid").create("fix1", "Fixed", bnd_2d)  # Boundary condition for bottom edge - no displacement
        h2storage.component("comp1").physics("solid").create("sym1", "SymmetrySolid", bnd_2d) # symmetry boundary condition 
        h2storage.component("comp1").physics("solid").feature("sym1").selection().named(f"geom1_{symmetry_bnd}")
        h2storage.component("comp1").physics("solid").create("bndl1", "BoundaryLoad", bnd_2d) # load boundary condition for storage once hydrogen storage is pressurizated  
        h2storage.component("comp1").physics("solid").feature("bndl1").selection().named(f"geom1_{storage_outer_bnd_2d}_bnd")
        h2storage.component("comp1").physics("solid").create("tl1", "ThinLayer", bnd_2d) #create lining boundary layer at the storage boundary
        h2storage.component("comp1").physics("solid").feature("tl1").selection().named(f"geom1_{storage_outer_bnd_2d}_bnd")
    elif model_dimension == "3d":
        if criterion == "hoek-brown":
            h2storage.component("comp1").physics("solid").feature("lemm1").create("rock1", "Rocks", dmn_3d) #Rock mass Hoek-Brown criteria    
            h2storage.component("comp1").physics("solid").feature("lemm1").feature("rock1").label("Rock mass - Hoek-Brown")
        elif criterion == "mohr-coulomb":
            h2storage.component("comp1").physics("solid").feature("lemm1").create("soil1", "SoilModel", dmn_3d)
            h2storage.component("comp1").physics("solid").feature("lemm1").feature("soil1").set("YieldCriterion", "MohrCoulomb")
            h2storage.component("comp1").physics("solid").feature("lemm1").feature("soil1").label("Rock mass - Mohr-Coulomb")
        h2storage.component("comp1").physics("solid").feature("lemm1").create("iss1", "InitialStressandStrain", dmn_3d)
        h2storage.component("comp1").physics("solid").feature("lemm1").create("act1", "Activation", dmn_3d)
        h2storage.component("comp1").physics("solid").feature("lemm1").feature("act1").selection().named(f"geom1_{h2storage_sel_3d}_dom")
        h2storage.component("comp1").physics("solid").create("roll1", "Roller", bnd_3d)  # Boundary condition for outer edge - no displacement in x-directio
        h2storage.component("comp1").physics("solid").feature("roll1").selection().named(f"geom1_{faraway_bnd_sel}_bnd")    
        h2storage.component("comp1").physics("solid").create("fix1", "Fixed", bnd_3d)  # Boundary condition for bottom edge - no displacement
        h2storage.component("comp1").physics("solid").feature("fix1").selection().named(f"geom1_{bottom_bnd_3d}")
        h2storage.component("comp1").physics("solid").create("sym1", "SymmetrySolid", bnd_3d) # symmetry boundary condition 
        h2storage.component("comp1").physics("solid").feature("sym1").selection().named(f"geom1_{symmetry_bnd_sel}_bnd")
        h2storage.component("comp1").physics("solid").create("bndl1", "BoundaryLoad", bnd_3d) # load boundary condition for storage once hydrogen storage is pressurizated  
        h2storage.component("comp1").physics("solid").feature("bndl1").selection().named(f"geom1_{storage_outer_bnd_3d}_bnd")
        h2storage.component("comp1").physics("solid").create("tl1", "ThinLayer", bnd_3d) #create lining boundary layer at the storage boundary
        h2storage.component("comp1").physics("solid").feature("tl1").selection().named(f"geom1_{storage_outer_bnd_3d}_bnd")
        h2storage.component("comp1").physics("solid").prop("ShapeProperty").set("order_displacement", 1)
    h2storage.component("comp1").physics("solid").feature("lemm1").feature("iss1").set("Sil", ("withsol('sol1', solid.sx)", "withsol('sol1', solid.sxy)", "withsol('sol1', solid.sxz)", "withsol('sol1', solid.sxy)", "withsol('sol1', solid.sy)", "withsol('sol1', solid.syz)", "withsol('sol1', solid.sxz)", "withsol('sol1', solid.syz)", "withsol('sol1', solid.sz)"))
    h2storage.component("comp1").physics("solid").create("gacc1", "GravityAcceleration", -1)
    h2storage.component("comp1").physics("solid").feature("bndl1").label("Storage internal pressure load") #Normal load
    h2storage.component("comp1").physics("solid").feature("bndl1").set("LoadType", "FollowerPressure")
    h2storage.component("comp1").physics("solid").feature("bndl1").set("FollowerPressure", "-int_pressure")
    h2storage.component("comp1").physics("solid").feature("tl1").label("Lining_boundary_condition") # Lining layer by boundary condition
    h2storage.component("comp1").physics("solid").feature("tl1").set("lth", "l_thickness")
    
    print("Done")
    ##################################################################################
    #Set up mesh
    ##################################################################################
    print("Setting up mesh...", end=" ")
    if model_dimension == "2d":
        h2storage.component("comp1").mesh("mesh1").create("edg1", "Edge")
        h2storage.component("comp1").mesh("mesh1").feature("edg1").selection().named(f"geom1_{storage_outer_bnd_2d}_bnd")
        h2storage.component("comp1").mesh("mesh1").feature("edg1").create("dis1", "Distribution")
        h2storage.component("comp1").mesh("mesh1").feature("edg1").feature("dis1").set("numelem", "num_elem")
        h2storage.component("comp1").mesh("mesh1").create("ftri1", "FreeTri")
        h2storage.component("comp1").mesh("mesh1").feature("ftri1").create("size1", "Size")
        h2storage.component("comp1").mesh("mesh1").feature("ftri1").feature("size1").set("custom", "on")
        h2storage.component("comp1").mesh("mesh1").feature("ftri1").feature("size1").set("hmaxactive", "on")
        h2storage.component("comp1").mesh("mesh1").feature("ftri1").feature("size1").set("hmax", "max_elem")
        h2storage.component("comp1").mesh("mesh1").feature("ftri1").feature("size1").set("hgradactive", "on")
        h2storage.component("comp1").mesh("mesh1").feature("ftri1").feature("size1").set("hgrad", "max_growth")
        h2storage.component("comp1").mesh("mesh1").run()
    elif model_dimension == "3d":
        h2storage.component("comp1").mesh("mesh1").create("edg1", "Edge");
        h2storage.component("comp1").mesh("mesh1").feature("edg1").selection().named(f"geom1_{h2storage_sel_3d}_edg")
        h2storage.component("comp1").mesh("mesh1").feature("edg1").create("dis1", "Distribution")
        h2storage.component("comp1").mesh("mesh1").feature("edg1").feature("dis1").set("numelem", "num_elem")
        h2storage.component("comp1").mesh("mesh1").create("ftet1", "FreeTet")
        h2storage.component("comp1").mesh("mesh1").feature("ftet1").selection().geom("geom1", dmn_3d)
        h2storage.component("comp1").mesh("mesh1").feature("ftet1").selection().named(f"geom1_{h2storage_sel_3d}_dom")
        h2storage.component("comp1").mesh("mesh1").feature("ftet1").create("size1", "Size")
        h2storage.component("comp1").mesh("mesh1").feature("ftet1").feature("size1").set("custom", "on")
        h2storage.component("comp1").mesh("mesh1").feature("ftet1").feature("size1").set("hgradactive", "on")
        h2storage.component("comp1").mesh("mesh1").feature("ftet1").feature("size1").set("hgrad", "max_growth")
        h2storage.component("comp1").mesh("mesh1").create("ftet2", "FreeTet")
        h2storage.component("comp1").mesh("mesh1").feature("ftet2").create("size1", "Size")
        h2storage.component("comp1").mesh("mesh1").feature("ftet2").feature("size1").set("custom", "on");
        h2storage.component("comp1").mesh("mesh1").feature("ftet2").feature("size1").set("hmaxactive", "on")
        h2storage.component("comp1").mesh("mesh1").feature("ftet2").feature("size1").set("hmax", "max_elem")
        h2storage.component("comp1").mesh("mesh1").feature("ftet2").feature("size1").set("hgradactive", "on")
        h2storage.component("comp1").mesh("mesh1").feature("ftet2").feature("size1").set("hgrad", "max_growth")
    print("Done")
    ##################################################################################
    #Create study
    ##################################################################################
    ##Initial condition before storage excavation
    print("Setting up study...", end=" ")
    h2storage.study().create("std1")
    h2storage.study("std1").create("stat", "Stationary")
    h2storage.study("std1").label("Study: Before h2storage excavation")
    h2storage.study("std1").feature("stat").setSolveFor("/physics/solid", True)
    h2storage.study("std1").feature("stat").set("useadvanceddisable", "on")
    h2storage.study("std1").feature("stat").set("disabledphysics", ("solid/lemm1/iss1", "solid/lemm1/act1", "solid/bndl1", "solid/tl1"))

    ##After storage excavation
    h2storage.study().create("std2")
    h2storage.study("std2").create("stat", "Stationary")
    h2storage.study("std2").label("Study: After h2storage excavation")
    h2storage.study("std2").feature("stat").setSolveFor("/physics/solid", True)
    if model_dimension == "2d":
        pymodel.save('2d_h2storage_model')
    elif model_dimension == "3d":
        pymodel.save('3d_h2storage_model')
    print("Done")
    
h2_storage_model = create_h2storagemodel("mohr-coulomb", "3d")
