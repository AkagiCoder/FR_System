#include <stdint.h>
#include "I2C.h"

#ifndef MPU6050_H_
#define MPU6050_H_
// MACROS
#define MPU_ADDR			0x68
#define MPU_ACCEL			0x3B

// Function Declarations
void MPU_init(void);
void MPU_ReadAccel(uint16_t accel[]);
#endif /* MPU6050_H_ */