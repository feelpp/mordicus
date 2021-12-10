/*!
* \file   IsotropicLinearHardeningMises-generic.cxx
* \brief  This file implements the umat interface for the IsotropicLinearHardeningMises behaviour law
* \author 
* \date   
*/

#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif /* NOMINMAX */
#include <windows.h>
#ifdef small
#undef small
#endif /* small */
#endif /* _WIN32 */

#ifndef MFRONT_SHAREDOBJ
#define MFRONT_SHAREDOBJ TFEL_VISIBILITY_EXPORT
#endif /* MFRONT_SHAREDOBJ */

#include<iostream>
#include<cstdlib>
#include"TFEL/Material/OutOfBoundsPolicy.hxx"
#include"TFEL/Math/t2tot2.hxx"
#include"TFEL/Math/t2tost2.hxx"
#include"TFEL/Material/IsotropicLinearHardeningMises.hxx"
#include"MFront/GenericBehaviour/Integrate.hxx"

#include"MFront/GenericBehaviour/IsotropicLinearHardeningMises-generic.hxx"

static tfel::material::OutOfBoundsPolicy&
IsotropicLinearHardeningMises_getOutOfBoundsPolicy(){
using namespace tfel::material;
static OutOfBoundsPolicy policy = None;
return policy;
}

#ifdef __cplusplus
extern "C"{
#endif /* __cplusplus */

MFRONT_SHAREDOBJ const char* 
IsotropicLinearHardeningMises_build_id = "";

MFRONT_SHAREDOBJ const char* 
IsotropicLinearHardeningMises_mfront_ept = "IsotropicLinearHardeningMises";

MFRONT_SHAREDOBJ const char* 
IsotropicLinearHardeningMises_tfel_version = "4.0.0";

MFRONT_SHAREDOBJ unsigned short IsotropicLinearHardeningMises_mfront_mkt = 1u;

MFRONT_SHAREDOBJ const char *
IsotropicLinearHardeningMises_mfront_interface = "Generic";

MFRONT_SHAREDOBJ const char *
IsotropicLinearHardeningMises_src = "IsotropicLinearHardeningMises.mfront";

MFRONT_SHAREDOBJ unsigned short IsotropicLinearHardeningMises_nModellingHypotheses = 5u;

MFRONT_SHAREDOBJ const char * 
IsotropicLinearHardeningMises_ModellingHypotheses[5u] = {"AxisymmetricalGeneralisedPlaneStrain",
"Axisymmetrical",
"PlaneStrain",
"GeneralisedPlaneStrain",
"Tridimensional"};

MFRONT_SHAREDOBJ unsigned short IsotropicLinearHardeningMises_nMainVariables = 1;
MFRONT_SHAREDOBJ unsigned short IsotropicLinearHardeningMises_nGradients = 1;

MFRONT_SHAREDOBJ int IsotropicLinearHardeningMises_GradientsTypes[1] = {1};
MFRONT_SHAREDOBJ const char * IsotropicLinearHardeningMises_Gradients[1] = {"Strain"};
MFRONT_SHAREDOBJ unsigned short IsotropicLinearHardeningMises_nThermodynamicForces = 1;

MFRONT_SHAREDOBJ int IsotropicLinearHardeningMises_ThermodynamicForcesTypes[1] = {1};
MFRONT_SHAREDOBJ const char * IsotropicLinearHardeningMises_ThermodynamicForces[1] = {"Stress"};
MFRONT_SHAREDOBJ unsigned short IsotropicLinearHardeningMises_nTangentOperatorBlocks = 2;

MFRONT_SHAREDOBJ const char * IsotropicLinearHardeningMises_TangentOperatorBlocks[2] = {"Stress",
"Strain"};
MFRONT_SHAREDOBJ unsigned short IsotropicLinearHardeningMises_BehaviourType = 1u;

MFRONT_SHAREDOBJ unsigned short IsotropicLinearHardeningMises_BehaviourKinematic = 1u;

MFRONT_SHAREDOBJ unsigned short IsotropicLinearHardeningMises_SymmetryType = 0u;

MFRONT_SHAREDOBJ unsigned short IsotropicLinearHardeningMises_ElasticSymmetryType = 0u;

MFRONT_SHAREDOBJ unsigned short IsotropicLinearHardeningMises_api_version = 1u;

MFRONT_SHAREDOBJ unsigned short IsotropicLinearHardeningMises_UsableInPurelyImplicitResolution = 1;

MFRONT_SHAREDOBJ unsigned short IsotropicLinearHardeningMises_nMaterialProperties = 0u;

MFRONT_SHAREDOBJ const char * const *IsotropicLinearHardeningMises_MaterialProperties = nullptr;

MFRONT_SHAREDOBJ unsigned short IsotropicLinearHardeningMises_nInternalStateVariables = 2;
MFRONT_SHAREDOBJ const char * IsotropicLinearHardeningMises_InternalStateVariables[2] = {"ElasticStrain",
"EquivalentPlasticStrain"};
MFRONT_SHAREDOBJ int IsotropicLinearHardeningMises_InternalStateVariablesTypes [] = {1,0};

MFRONT_SHAREDOBJ unsigned short IsotropicLinearHardeningMises_nExternalStateVariables = 0;
MFRONT_SHAREDOBJ const char * const * IsotropicLinearHardeningMises_ExternalStateVariables = nullptr;

MFRONT_SHAREDOBJ unsigned short IsotropicLinearHardeningMises_nParameters = 6;
MFRONT_SHAREDOBJ const char * IsotropicLinearHardeningMises_Parameters[6] = {"YoungModulus",
"PoissonRatio","HardeningSlope","YieldStrength","minimal_time_step_scaling_factor","maximal_time_step_scaling_factor"};
MFRONT_SHAREDOBJ int IsotropicLinearHardeningMises_ParametersTypes [] = {0,0,0,0,0,0};

MFRONT_SHAREDOBJ double IsotropicLinearHardeningMises_YoungModulus_ParameterDefaultValue = 200000;

MFRONT_SHAREDOBJ double IsotropicLinearHardeningMises_PoissonRatio_ParameterDefaultValue = 0.2;

MFRONT_SHAREDOBJ double IsotropicLinearHardeningMises_HardeningSlope_ParameterDefaultValue = 100;

MFRONT_SHAREDOBJ double IsotropicLinearHardeningMises_YieldStrength_ParameterDefaultValue = 10;

MFRONT_SHAREDOBJ double IsotropicLinearHardeningMises_minimal_time_step_scaling_factor_ParameterDefaultValue = 0.1;

MFRONT_SHAREDOBJ double IsotropicLinearHardeningMises_maximal_time_step_scaling_factor_ParameterDefaultValue = 1.7976931348623e+308;

MFRONT_SHAREDOBJ unsigned short IsotropicLinearHardeningMises_requiresStiffnessTensor = 0;
MFRONT_SHAREDOBJ unsigned short IsotropicLinearHardeningMises_requiresThermalExpansionCoefficientTensor = 0;
MFRONT_SHAREDOBJ unsigned short IsotropicLinearHardeningMises_nInitializeFunctions= 0;

MFRONT_SHAREDOBJ const char * const * IsotropicLinearHardeningMises_InitializeFunctions = nullptr;


MFRONT_SHAREDOBJ unsigned short IsotropicLinearHardeningMises_ComputesInternalEnergy = 0;

MFRONT_SHAREDOBJ unsigned short IsotropicLinearHardeningMises_ComputesDissipatedEnergy = 0;

MFRONT_SHAREDOBJ void
IsotropicLinearHardeningMises_setOutOfBoundsPolicy(const int p){
if(p==0){
IsotropicLinearHardeningMises_getOutOfBoundsPolicy() = tfel::material::None;
} else if(p==1){
IsotropicLinearHardeningMises_getOutOfBoundsPolicy() = tfel::material::Warning;
} else if(p==2){
IsotropicLinearHardeningMises_getOutOfBoundsPolicy() = tfel::material::Strict;
} else {
std::cerr << "IsotropicLinearHardeningMises_setOutOfBoundsPolicy: invalid argument\n";
}
}

MFRONT_SHAREDOBJ int
IsotropicLinearHardeningMises_setParameter(const char *const key,const double value){
using tfel::material::IsotropicLinearHardeningMisesParametersInitializer;
auto& i = IsotropicLinearHardeningMisesParametersInitializer::get();
try{
i.set(key,value);
} catch(std::runtime_error& e){
std::cerr << e.what() << std::endl;
return 0;
}
return 1;
}

MFRONT_SHAREDOBJ int IsotropicLinearHardeningMises_AxisymmetricalGeneralisedPlaneStrain(mfront_gb_BehaviourData* const d){
using namespace tfel::material;
using real = mfront::gb::real;
constexpr auto h = ModellingHypothesis::AXISYMMETRICALGENERALISEDPLANESTRAIN;
using Behaviour = IsotropicLinearHardeningMises<h,real,false>;
const auto r = mfront::gb::integrate<Behaviour>(*d,Behaviour::STANDARDTANGENTOPERATOR, IsotropicLinearHardeningMises_getOutOfBoundsPolicy());
return r;
} // end of IsotropicLinearHardeningMises_AxisymmetricalGeneralisedPlaneStrain

MFRONT_SHAREDOBJ int IsotropicLinearHardeningMises_Axisymmetrical(mfront_gb_BehaviourData* const d){
using namespace tfel::material;
using real = mfront::gb::real;
constexpr auto h = ModellingHypothesis::AXISYMMETRICAL;
using Behaviour = IsotropicLinearHardeningMises<h,real,false>;
const auto r = mfront::gb::integrate<Behaviour>(*d,Behaviour::STANDARDTANGENTOPERATOR, IsotropicLinearHardeningMises_getOutOfBoundsPolicy());
return r;
} // end of IsotropicLinearHardeningMises_Axisymmetrical

MFRONT_SHAREDOBJ int IsotropicLinearHardeningMises_PlaneStrain(mfront_gb_BehaviourData* const d){
using namespace tfel::material;
using real = mfront::gb::real;
constexpr auto h = ModellingHypothesis::PLANESTRAIN;
using Behaviour = IsotropicLinearHardeningMises<h,real,false>;
const auto r = mfront::gb::integrate<Behaviour>(*d,Behaviour::STANDARDTANGENTOPERATOR, IsotropicLinearHardeningMises_getOutOfBoundsPolicy());
return r;
} // end of IsotropicLinearHardeningMises_PlaneStrain

MFRONT_SHAREDOBJ int IsotropicLinearHardeningMises_GeneralisedPlaneStrain(mfront_gb_BehaviourData* const d){
using namespace tfel::material;
using real = mfront::gb::real;
constexpr auto h = ModellingHypothesis::GENERALISEDPLANESTRAIN;
using Behaviour = IsotropicLinearHardeningMises<h,real,false>;
const auto r = mfront::gb::integrate<Behaviour>(*d,Behaviour::STANDARDTANGENTOPERATOR, IsotropicLinearHardeningMises_getOutOfBoundsPolicy());
return r;
} // end of IsotropicLinearHardeningMises_GeneralisedPlaneStrain

MFRONT_SHAREDOBJ int IsotropicLinearHardeningMises_Tridimensional(mfront_gb_BehaviourData* const d){
using namespace tfel::material;
using real = mfront::gb::real;
constexpr auto h = ModellingHypothesis::TRIDIMENSIONAL;
using Behaviour = IsotropicLinearHardeningMises<h,real,false>;
const auto r = mfront::gb::integrate<Behaviour>(*d,Behaviour::STANDARDTANGENTOPERATOR, IsotropicLinearHardeningMises_getOutOfBoundsPolicy());
return r;
} // end of IsotropicLinearHardeningMises_Tridimensional

#ifdef __cplusplus
}
#endif /* __cplusplus */

