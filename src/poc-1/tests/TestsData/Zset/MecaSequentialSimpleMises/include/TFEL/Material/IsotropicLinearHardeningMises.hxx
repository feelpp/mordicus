/*!
* \file   TFEL/Material/IsotropicLinearHardeningMises.hxx
* \brief  this file implements the IsotropicLinearHardeningMises Behaviour.
*         File generated by tfel version 4.0.0
 */

#ifndef LIB_TFELMATERIAL_ISOTROPICLINEARHARDENINGMISES_HXX
#define LIB_TFELMATERIAL_ISOTROPICLINEARHARDENINGMISES_HXX

#include<string>
#include<iostream>
#include<limits>
#include<stdexcept>
#include<algorithm>

#include"TFEL/Raise.hxx"
#include"TFEL/PhysicalConstants.hxx"
#include"TFEL/Config/TFELConfig.hxx"
#include"TFEL/Config/TFELTypes.hxx"
#include"TFEL/TypeTraits/IsFundamentalNumericType.hxx"
#include"TFEL/TypeTraits/IsReal.hxx"
#include"TFEL/Math/General/IEEE754.hxx"
#include"TFEL/Material/MaterialException.hxx"
#include"TFEL/Material/MechanicalBehaviour.hxx"
#include"TFEL/Material/MechanicalBehaviourTraits.hxx"
#include"TFEL/Material/OutOfBoundsPolicy.hxx"
#include"TFEL/Material/BoundsCheck.hxx"
#include"TFEL/Material/IsotropicPlasticity.hxx"
#include"TFEL/Material/Lame.hxx"
#include"TFEL/Material/Hosford1972YieldCriterion.hxx"
#include"TFEL/Material/IsotropicLinearHardeningMisesBehaviourData.hxx"
#include"TFEL/Material/IsotropicLinearHardeningMisesIntegrationData.hxx"

#include "MFront/GenericBehaviour/State.hxx"
#include "MFront/GenericBehaviour/BehaviourData.hxx"
namespace tfel::material{

struct IsotropicLinearHardeningMisesParametersInitializer
{
static IsotropicLinearHardeningMisesParametersInitializer&
get();

double young;
double nu;
double H;
double s0;
double minimal_time_step_scaling_factor;
double maximal_time_step_scaling_factor;

void set(const char* const,const double);

/*!
 * \brief convert a string to double
 * \param[in] p : parameter
 * \param[in] v : value
 */
static double getDouble(const std::string&,const std::string&);
private :

IsotropicLinearHardeningMisesParametersInitializer();

IsotropicLinearHardeningMisesParametersInitializer(const IsotropicLinearHardeningMisesParametersInitializer&);

IsotropicLinearHardeningMisesParametersInitializer&
operator=(const IsotropicLinearHardeningMisesParametersInitializer&);
/*!
 * \brief read the parameters from the given file
 * \param[out] pi : parameters initializer
 * \param[in]  fn : file name
 */
static void readParameters(IsotropicLinearHardeningMisesParametersInitializer&,const char* const);
};

//! \brief forward declaration
template<ModellingHypothesis::Hypothesis, typename NumericType, bool use_qt>
struct IsotropicLinearHardeningMises;

//! \brief forward declaration
template<ModellingHypothesis::Hypothesis hypothesis, typename NumericType>
std::ostream&
 operator <<(std::ostream&,const IsotropicLinearHardeningMises<hypothesis, NumericType, false>&);

/*!
* \class IsotropicLinearHardeningMises
* \brief This class implements the IsotropicLinearHardeningMises behaviour.
* \tparam hypothesis: modelling hypothesis.
* \tparam NumericType: numerical type.
*/
template<ModellingHypothesis::Hypothesis hypothesis,typename NumericType>
struct IsotropicLinearHardeningMises<hypothesis, NumericType, false> final
: public MechanicalBehaviour<MechanicalBehaviourBase::STANDARDSTRAINBASEDBEHAVIOUR,hypothesis, NumericType, false>,
public IsotropicLinearHardeningMisesBehaviourData<hypothesis, NumericType, false>,
public IsotropicLinearHardeningMisesIntegrationData<hypothesis, NumericType, false>
{

static constexpr unsigned short N = ModellingHypothesisToSpaceDimension<hypothesis>::value;

static_assert(N==1||N==2||N==3);
static_assert(tfel::typetraits::IsFundamentalNumericType<NumericType>::cond);
static_assert(tfel::typetraits::IsReal<NumericType>::cond);

friend std::ostream& operator<< <>(std::ostream&,const IsotropicLinearHardeningMises&);

static constexpr unsigned short TVectorSize = N;
typedef tfel::math::StensorDimeToSize<N> StensorDimeToSize;
static constexpr unsigned short StensorSize = StensorDimeToSize::value;
typedef tfel::math::TensorDimeToSize<N> TensorDimeToSize;
static constexpr unsigned short TensorSize = TensorDimeToSize::value;

using ushort =  unsigned short;
using Types = tfel::config::Types<N, NumericType, false>;
using Type = NumericType;
using real = typename Types::real;
using time = typename Types::time;
using length = typename Types::length;
using frequency = typename Types::frequency;
using speed = typename Types::speed;
using stress = typename Types::stress;
using strain = typename Types::strain;
using strainrate = typename Types::strainrate;
using stressrate = typename Types::stressrate;
using temperature = typename Types::temperature;
using thermalexpansion = typename Types::thermalexpansion;
using thermalconductivity = typename Types::thermalconductivity;
using massdensity = typename Types::massdensity;
using energydensity = typename Types::energydensity;
using TVector = typename Types::TVector;
using DisplacementTVector = typename Types::DisplacementTVector;
using ForceTVector = typename Types::ForceTVector;
using HeatFlux = typename Types::HeatFlux;
using TemperatureGradient = typename Types::TemperatureGradient;
using Stensor = typename Types::Stensor;
using StressStensor = typename Types::StressStensor;
using StressRateStensor = typename Types::StressRateStensor;
using StrainStensor = typename Types::StrainStensor;
using StrainRateStensor = typename Types::StrainRateStensor;
using FrequencyStensor = typename Types::FrequencyStensor;
using Tensor = typename Types::Tensor;
using DeformationGradientTensor = typename Types::DeformationGradientTensor;
using StressTensor = typename Types::StressTensor;
using StiffnessTensor = typename Types::StiffnessTensor;
using Stensor4 = typename Types::Stensor4;
using TangentOperator = StiffnessTensor;
using PhysicalConstants = tfel::PhysicalConstants<NumericType, false>;

public :

typedef IsotropicLinearHardeningMisesBehaviourData<hypothesis, NumericType, false> BehaviourData;
typedef IsotropicLinearHardeningMisesIntegrationData<hypothesis, NumericType, false> IntegrationData;
typedef typename MechanicalBehaviour<MechanicalBehaviourBase::STANDARDSTRAINBASEDBEHAVIOUR,hypothesis, NumericType, false>::SMFlag SMFlag;
typedef typename MechanicalBehaviour<MechanicalBehaviourBase::STANDARDSTRAINBASEDBEHAVIOUR,hypothesis, NumericType, false>::SMType SMType;
using MechanicalBehaviour<MechanicalBehaviourBase::STANDARDSTRAINBASEDBEHAVIOUR,hypothesis, NumericType, false>::ELASTIC;
using MechanicalBehaviour<MechanicalBehaviourBase::STANDARDSTRAINBASEDBEHAVIOUR,hypothesis, NumericType, false>::SECANTOPERATOR;
using MechanicalBehaviour<MechanicalBehaviourBase::STANDARDSTRAINBASEDBEHAVIOUR,hypothesis, NumericType, false>::TANGENTOPERATOR;
using MechanicalBehaviour<MechanicalBehaviourBase::STANDARDSTRAINBASEDBEHAVIOUR,hypothesis, NumericType, false>::CONSISTENTTANGENTOPERATOR;
using MechanicalBehaviour<MechanicalBehaviourBase::STANDARDSTRAINBASEDBEHAVIOUR,hypothesis, NumericType, false>::NOSTIFFNESSREQUESTED;
using MechanicalBehaviour<MechanicalBehaviourBase::STANDARDSTRAINBASEDBEHAVIOUR,hypothesis, NumericType, false>::STANDARDTANGENTOPERATOR;
using IntegrationResult = typename MechanicalBehaviour<MechanicalBehaviourBase::STANDARDSTRAINBASEDBEHAVIOUR,hypothesis, NumericType, false>::IntegrationResult;

using MechanicalBehaviour<MechanicalBehaviourBase::STANDARDSTRAINBASEDBEHAVIOUR,hypothesis, NumericType, false>::SUCCESS;
using MechanicalBehaviour<MechanicalBehaviourBase::STANDARDSTRAINBASEDBEHAVIOUR,hypothesis, NumericType, false>::FAILURE;
using MechanicalBehaviour<MechanicalBehaviourBase::STANDARDSTRAINBASEDBEHAVIOUR,hypothesis, NumericType, false>::UNRELIABLE_RESULTS;

using StressFreeExpansionType = StrainStensor;

private :



#line 4 "IsotropicLinearHardeningMises.mfront"
StrainStensor deel;
#line 6 "IsotropicLinearHardeningMises.mfront"
strain dp;


#line 9 "IsotropicLinearHardeningMises.mfront"
real young;
#line 11 "IsotropicLinearHardeningMises.mfront"
real nu;
#line 13 "IsotropicLinearHardeningMises.mfront"
real H;
#line 15 "IsotropicLinearHardeningMises.mfront"
real s0;
time minimal_time_step_scaling_factor;
time maximal_time_step_scaling_factor;

//! Tangent operator;
TangentOperator Dt;
//! alias to the tangent operator;
TangentOperator& dsig_ddeto;
/*!
* \brief Update internal variables at end of integration
*/
void updateIntegrationVariables(){
}

/*!
* \brief Update internal variables at end of integration
*/
void updateStateVariables(){
this->eel += this->deel;
this->p += this->dp;
}

/*!
* \brief Update auxiliary state variables at end of integration
*/
void updateAuxiliaryStateVariables()
{}

//! \brief Default constructor (disabled)
IsotropicLinearHardeningMises() =delete ;
//! \brief Copy constructor (disabled)
IsotropicLinearHardeningMises(const IsotropicLinearHardeningMises&) = delete;
//! \brief Assignement operator (disabled)
IsotropicLinearHardeningMises& operator = (const IsotropicLinearHardeningMises&) = delete;

public:

/*!
* \brief Constructor
*/
IsotropicLinearHardeningMises(const IsotropicLinearHardeningMisesBehaviourData<hypothesis, NumericType, false>& src1,
const IsotropicLinearHardeningMisesIntegrationData<hypothesis, NumericType, false>& src2)
: IsotropicLinearHardeningMisesBehaviourData<hypothesis, NumericType, false>(src1),
IsotropicLinearHardeningMisesIntegrationData<hypothesis, NumericType, false>(src2),
deel(typename tfel::math::MathObjectTraits<StrainStensor>::NumType(0)),
dp(strain(0)),
dsig_ddeto(Dt)
{
using namespace std;
using namespace tfel::math;
using std::vector;
this->young = IsotropicLinearHardeningMisesParametersInitializer::get().young;
this->nu = IsotropicLinearHardeningMisesParametersInitializer::get().nu;
this->H = IsotropicLinearHardeningMisesParametersInitializer::get().H;
this->s0 = IsotropicLinearHardeningMisesParametersInitializer::get().s0;
this->minimal_time_step_scaling_factor = IsotropicLinearHardeningMisesParametersInitializer::get().minimal_time_step_scaling_factor;
this->maximal_time_step_scaling_factor = IsotropicLinearHardeningMisesParametersInitializer::get().maximal_time_step_scaling_factor;
}

/*
 * \brief constructor for the Generic interface
 * \param[in] mgb_d: behaviour data
 */
IsotropicLinearHardeningMises(const mfront::gb::BehaviourData& mgb_d)
: IsotropicLinearHardeningMisesBehaviourData<hypothesis, NumericType, false>(mgb_d),
IsotropicLinearHardeningMisesIntegrationData<hypothesis, NumericType, false>(mgb_d),
deel(typename tfel::math::MathObjectTraits<StrainStensor>::NumType(0)),
dp(strain(0)),
dsig_ddeto(Dt)
{
using namespace std;
using namespace tfel::math;
using std::vector;
this->young = IsotropicLinearHardeningMisesParametersInitializer::get().young;
this->nu = IsotropicLinearHardeningMisesParametersInitializer::get().nu;
this->H = IsotropicLinearHardeningMisesParametersInitializer::get().H;
this->s0 = IsotropicLinearHardeningMisesParametersInitializer::get().s0;
this->minimal_time_step_scaling_factor = IsotropicLinearHardeningMisesParametersInitializer::get().minimal_time_step_scaling_factor;
this->maximal_time_step_scaling_factor = IsotropicLinearHardeningMisesParametersInitializer::get().maximal_time_step_scaling_factor;
this-> eto = tfel::math::map<StrainStensor>(mgb_d.s0.gradients);
tfel::fsalgo::transform<StensorSize>::exe(mgb_d.s1.gradients,mgb_d.s0.gradients,this->deto.begin(),std::minus<real>());
this-> sig = tfel::math::map<StressStensor>(mgb_d.s0.thermodynamic_forces);
}

/*!
 * \ brief initialize the behaviour with user code
 */
void initialize(){
using namespace std;
using namespace tfel::math;
using std::vector;
}

/*!
* \brief set the policy for "out of bounds" conditions
*/
void
setOutOfBoundsPolicy(const OutOfBoundsPolicy policy_value){
this->policy = policy_value;
} // end of setOutOfBoundsPolicy

/*!
* \return the modelling hypothesis
*/
constexpr ModellingHypothesis::Hypothesis
getModellingHypothesis() const{
return hypothesis;
} // end of getModellingHypothesis

/*!
* \brief check bounds
*/
void checkBounds() const{
} // end of checkBounds

IntegrationResult
computePredictionOperator(const SMFlag smflag,const SMType smt) override{
using namespace std;
using namespace tfel::math;
using std::vector;
tfel::raise_if(smflag!=MechanicalBehaviour<MechanicalBehaviourBase::STANDARDSTRAINBASEDBEHAVIOUR,hypothesis, NumericType, false>::STANDARDTANGENTOPERATOR,
"invalid prediction operator flag");
#line 27 "IsotropicLinearHardeningMises.mfront"
const auto lambda = computeLambda((this->young),(this->nu));
#line 28 "IsotropicLinearHardeningMises.mfront"
const auto mu     = computeMu((this->young),(this->nu));
#line 29 "IsotropicLinearHardeningMises.mfront"
(this->Dt) = lambda*Stensor4::IxI()+2*mu*Stensor4::Id();return SUCCESS;
}

time getMinimalTimeStepScalingFactor() const noexcept override{
  return this->minimal_time_step_scaling_factor;
}

std::pair<bool, time>
computeAPrioriTimeStepScalingFactor(const time current_time_step_scaling_factor) const override{
const auto time_scaling_factor = this->computeAPrioriTimeStepScalingFactorII();
return {time_scaling_factor.first,
        std::min(std::min(std::max(time_scaling_factor.second,
                                   this->minimal_time_step_scaling_factor),
                          this->maximal_time_step_scaling_factor),
                  current_time_step_scaling_factor)};
}

/*!
* \brief Integrate behaviour  over the time step
*/
IntegrationResult
integrate(const SMFlag smflag, const SMType smt) override{
using namespace std;
using namespace tfel::math;
raise_if(smflag!=MechanicalBehaviour<MechanicalBehaviourBase::STANDARDSTRAINBASEDBEHAVIOUR,hypothesis, NumericType, false>::STANDARDTANGENTOPERATOR,
"invalid tangent operator flag");
bool computeTangentOperator_ = smt!=NOSTIFFNESSREQUESTED;
#line 37 "IsotropicLinearHardeningMises.mfront"
const auto lambda = computeLambda(this->young,this->nu);
#line 38 "IsotropicLinearHardeningMises.mfront"
const auto mu     = computeMu(this->young,this->nu);
#line 39 "IsotropicLinearHardeningMises.mfront"
this->eel += this->deto;
#line 40 "IsotropicLinearHardeningMises.mfront"
const auto se     = 2*mu*deviator(this->eel);
#line 41 "IsotropicLinearHardeningMises.mfront"
const auto seq_e  = sigmaeq(se);
#line 42 "IsotropicLinearHardeningMises.mfront"
const auto b      = seq_e-this->s0-this->H*this->p>stress{0};
#line 43 "IsotropicLinearHardeningMises.mfront"
if(b){
#line 44 "IsotropicLinearHardeningMises.mfront"
const auto iseq_e = 1/seq_e;
#line 45 "IsotropicLinearHardeningMises.mfront"
const auto n      = eval(3*se/(2*seq_e));
#line 46 "IsotropicLinearHardeningMises.mfront"
const auto cste   = 1/(this->H+3*mu);
#line 47 "IsotropicLinearHardeningMises.mfront"
this->dp   = (seq_e-this->s0-this->H*this->p)*cste;
#line 48 "IsotropicLinearHardeningMises.mfront"
this->eel -= this->dp*n;
#line 49 "IsotropicLinearHardeningMises.mfront"
if(computeTangentOperator_){
#line 50 "IsotropicLinearHardeningMises.mfront"
if(smt==CONSISTENTTANGENTOPERATOR){
#line 51 "IsotropicLinearHardeningMises.mfront"
this->Dt = (lambda*Stensor4::IxI()+2*mu*Stensor4::Id()
#line 52 "IsotropicLinearHardeningMises.mfront"
-4*mu*mu*(this->dp*iseq_e*(Stensor4::M()-(n^n))+cste*(n^n)));
#line 53 "IsotropicLinearHardeningMises.mfront"
} else {
#line 54 "IsotropicLinearHardeningMises.mfront"
this->Dt = lambda*Stensor4::IxI()+2*mu*Stensor4::Id();
#line 55 "IsotropicLinearHardeningMises.mfront"
}
#line 56 "IsotropicLinearHardeningMises.mfront"
}
#line 57 "IsotropicLinearHardeningMises.mfront"
} else {
#line 58 "IsotropicLinearHardeningMises.mfront"
if(computeTangentOperator_){
#line 59 "IsotropicLinearHardeningMises.mfront"
this->Dt = lambda*Stensor4::IxI()+2*mu*Stensor4::Id();
#line 60 "IsotropicLinearHardeningMises.mfront"
}
#line 61 "IsotropicLinearHardeningMises.mfront"
}
#line 62 "IsotropicLinearHardeningMises.mfront"
this->sig = lambda*trace(this->eel)*Stensor::Id()+2*mu*this->eel;
this->updateIntegrationVariables();
this->updateStateVariables();
this->updateAuxiliaryStateVariables();
return MechanicalBehaviour<MechanicalBehaviourBase::STANDARDSTRAINBASEDBEHAVIOUR,hypothesis, NumericType, false>::SUCCESS;
}

std::pair<bool, time>
computeAPosterioriTimeStepScalingFactor(const time current_time_step_scaling_factor) const override{
const auto time_scaling_factor = this->computeAPosterioriTimeStepScalingFactorII();
return {time_scaling_factor.first,
        std::min(std::min(std::max(time_scaling_factor.second,
                                   this->minimal_time_step_scaling_factor),
                          this->maximal_time_step_scaling_factor),
                 current_time_step_scaling_factor)};
}

/*!
* \brief Update the internal energy at end of the time step
* \param[in] Psi_s: internal energy at end of the time step
*/
void computeInternalEnergy(real& Psi_s) const
{
Psi_s=0;
}

/*!
* \brief Update the dissipated energy at end of the time step
* \param[in] Psi_d: dissipated energy at end of the time step
*/
void computeDissipatedEnergy(real& Psi_d) const
{
Psi_d=0;
}

/*!
* \brief compute the sound velocity
* \param[in] rho_m0: mass density in the reference configuration
*/
speed computeSpeedOfSound(const massdensity&) const {
return speed(0);

}

const TangentOperator& getTangentOperator() const{
return this->Dt;
}

void updateExternalStateVariables(){
this->eto  += this->deto;
this->T += this->dT;
}

//!
~IsotropicLinearHardeningMises()
 override = default;

private:

std::pair<bool, time> computeAPrioriTimeStepScalingFactorII() const{
return {true, this->maximal_time_step_scaling_factor};
}

std::pair<bool, time> computeAPosterioriTimeStepScalingFactorII() const{
return {true,this->maximal_time_step_scaling_factor};
}

//! policy for treating out of bounds conditions
OutOfBoundsPolicy policy = None;
}; // end of IsotropicLinearHardeningMises class

template<ModellingHypothesis::Hypothesis hypothesis, typename NumericType>
std::ostream&
operator <<(std::ostream& os,const IsotropicLinearHardeningMises<hypothesis, NumericType, false>& b)
{
os << "εᵗᵒ : " << b.eto << '\n';
os << "Δεᵗᵒ : " << b.deto << '\n';
os << "σ : " << b.sig << '\n';
os << "Δt : " << b.dt << '\n';
os << "eel : " << b.eel << '\n';
os << "Δeel : " << b.deel << '\n';
os << "p : " << b.p << '\n';
os << "Δp : " << b.dp << '\n';
os << "T : " << b.T << '\n';
os << "ΔT : " << b.dT << '\n';
os << "young : " << b.young << '\n';
os << "nu : " << b.nu << '\n';
os << "H : " << b.H << '\n';
os << "s0 : " << b.s0 << '\n';
os << "minimal_time_step_scaling_factor : " << b.minimal_time_step_scaling_factor << '\n';
os << "maximal_time_step_scaling_factor : " << b.maximal_time_step_scaling_factor << '\n';
return os;
}

/*!
* Partial specialisation for IsotropicLinearHardeningMises.
*/
template<ModellingHypothesis::Hypothesis hypothesis, typename NumericType>
class MechanicalBehaviourTraits<IsotropicLinearHardeningMises<hypothesis, NumericType, false> >
{
using size_type = unsigned short;
static constexpr unsigned short N = ModellingHypothesisToSpaceDimension<hypothesis>::value;
static constexpr unsigned short TVectorSize = N;
typedef tfel::math::StensorDimeToSize<N> StensorDimeToSize;
static constexpr unsigned short StensorSize = StensorDimeToSize::value;
typedef tfel::math::TensorDimeToSize<N> TensorDimeToSize;
static constexpr unsigned short TensorSize = TensorDimeToSize::value;
public:
static constexpr bool is_defined = true;
static constexpr bool use_quantities = false;
static constexpr bool hasStressFreeExpansion = false;
static constexpr bool handlesThermalExpansion = false;
static constexpr unsigned short dimension = N;
static constexpr size_type material_properties_nb = 0;
static constexpr size_type internal_variables_nb  = StensorSize+1;
static constexpr size_type external_variables_nb  = 1;
static constexpr size_type external_variables_nb2 = 0;
static constexpr bool hasConsistentTangentOperator = true;
static constexpr bool isConsistentTangentOperatorSymmetric = true;
static constexpr bool hasPredictionOperator = true;
static constexpr bool hasAPrioriTimeStepScalingFactor = false;
static constexpr bool hasComputeInternalEnergy = false;
static constexpr bool hasComputeDissipatedEnergy = false;
/*!
* \return the name of the class.
*/
static const char* getName(){
return "IsotropicLinearHardeningMises";
}

};

/*!
* Partial specialisation for IsotropicLinearHardeningMises.
*/
template<typename NumericType>
class MechanicalBehaviourTraits<IsotropicLinearHardeningMises<ModellingHypothesis::AXISYMMETRICALGENERALISEDPLANESTRESS, NumericType, false> >
{
using size_type = unsigned short;
public:
static constexpr bool is_defined = false;
static constexpr bool use_quantities = false;
static constexpr bool hasStressFreeExpansion = false;
static constexpr bool handlesThermalExpansion = false;
static constexpr unsigned short dimension = 0u;
static constexpr size_type material_properties_nb = 0;
static constexpr size_type internal_variables_nb  = 0;
static constexpr size_type external_variables_nb  = 0;
static constexpr size_type external_variables_nb2 = 0;
static constexpr bool hasConsistentTangentOperator = false;
static constexpr bool isConsistentTangentOperatorSymmetric = false;
static constexpr bool hasPredictionOperator = false;
static constexpr bool hasAPrioriTimeStepScalingFactor = false;
static constexpr bool hasComputeInternalEnergy = false;
static constexpr bool hasComputeDissipatedEnergy = false;
/*!
* \return the name of the class.
*/
static const char* getName(){
return "IsotropicLinearHardeningMises";
}

};

/*!
* Partial specialisation for IsotropicLinearHardeningMises.
*/
template<typename NumericType>
class MechanicalBehaviourTraits<IsotropicLinearHardeningMises<ModellingHypothesis::PLANESTRESS, NumericType, false> >
{
using size_type = unsigned short;
public:
static constexpr bool is_defined = false;
static constexpr bool use_quantities = false;
static constexpr bool hasStressFreeExpansion = false;
static constexpr bool handlesThermalExpansion = false;
static constexpr unsigned short dimension = 0u;
static constexpr size_type material_properties_nb = 0;
static constexpr size_type internal_variables_nb  = 0;
static constexpr size_type external_variables_nb  = 0;
static constexpr size_type external_variables_nb2 = 0;
static constexpr bool hasConsistentTangentOperator = false;
static constexpr bool isConsistentTangentOperatorSymmetric = false;
static constexpr bool hasPredictionOperator = false;
static constexpr bool hasAPrioriTimeStepScalingFactor = false;
static constexpr bool hasComputeInternalEnergy = false;
static constexpr bool hasComputeDissipatedEnergy = false;
/*!
* \return the name of the class.
*/
static const char* getName(){
return "IsotropicLinearHardeningMises";
}

};

} // end of namespace tfel::material

#endif /* LIB_TFELMATERIAL_ISOTROPICLINEARHARDENINGMISES_HXX */
