/*!
* \file   IsotropicLinearHardeningMises-generic.hxx
* \brief  This file declares the umat interface for the IsotropicLinearHardeningMises behaviour law
* \author 
* \date   
*/

#ifndef LIB_GENERIC_ISOTROPICLINEARHARDENINGMISES_HXX
#define LIB_GENERIC_ISOTROPICLINEARHARDENINGMISES_HXX

#include"TFEL/Config/TFELConfig.hxx"
#include"MFront/GenericBehaviour/BehaviourData.h"

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

#ifdef __cplusplus
extern "C"{
#endif /* __cplusplus */

MFRONT_SHAREDOBJ void
IsotropicLinearHardeningMises_setOutOfBoundsPolicy(const int);

MFRONT_SHAREDOBJ int
IsotropicLinearHardeningMises_setParameter(const char *const,const double);

/*!
 * \param[in,out] d: material data
 */
MFRONT_SHAREDOBJ int IsotropicLinearHardeningMises_AxisymmetricalGeneralisedPlaneStrain(mfront_gb_BehaviourData* const);

/*!
 * \param[in,out] d: material data
 */
MFRONT_SHAREDOBJ int IsotropicLinearHardeningMises_Axisymmetrical(mfront_gb_BehaviourData* const);

/*!
 * \param[in,out] d: material data
 */
MFRONT_SHAREDOBJ int IsotropicLinearHardeningMises_PlaneStrain(mfront_gb_BehaviourData* const);

/*!
 * \param[in,out] d: material data
 */
MFRONT_SHAREDOBJ int IsotropicLinearHardeningMises_GeneralisedPlaneStrain(mfront_gb_BehaviourData* const);

/*!
 * \param[in,out] d: material data
 */
MFRONT_SHAREDOBJ int IsotropicLinearHardeningMises_Tridimensional(mfront_gb_BehaviourData* const);

#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif /* LIB_GENERIC_ISOTROPICLINEARHARDENINGMISES_HXX */
