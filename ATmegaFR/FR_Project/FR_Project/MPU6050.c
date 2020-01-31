#include "MPU6050.h"

// Wake up the MPU6050
void MPU_init(void)
{
	i2c_startMT(MPU_ADDR);				// Start transmit
	i2c_write(0x6B);					// Reg: PWR_MGMT_1
	i2c_write(0x00);					// Write 0 to wake up
	i2c_stop();							// Stop
}

// Read MPU acceleration values
void MPU_ReadAccel(uint16_t accel[])
{
	i2c_startMT(MPU_ADDR);				// Start transmit
	i2c_write(MPU_ACCEL);				// Reg: MPU_ACCEL
	i2c_startMR(MPU_ADDR);				// Start receiver
	// Read X-axis
	accel[0] = i2c_readACK() << 8;		// Upper byte
	accel[0] |= i2c_readACK();			// Lower byte
	// Read Y-axis
	accel[1] = i2c_readACK() << 8;		// Upper byte
	accel[1] |= i2c_readACK();			// Lower byte
	// Read Z-axis
	accel[2] = i2c_readACK() << 8;		// Upper byte
	accel[2] |= i2c_readNACK();			// Lower byte
	i2c_stop();							// Stop
}