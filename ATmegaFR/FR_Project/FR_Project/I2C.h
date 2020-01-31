#include <avr/io.h>
#include <stdint.h>

#ifndef I2C_H_
#define I2C_H_
// Function declarations
void i2c_init(void);					// Initiate the I2C on ATmega328
void i2c_write(unsigned char data);		// Write to the I2C
void i2c_startMT(uint8_t addr);			// Master transmit start
void i2c_startMR(uint8_t addr);			// Master receive start
void i2c_stop(void);					// Stop condition
uint8_t i2c_readACK(void);				// Read from the I2C and ACK
uint8_t i2c_readNACK(void);				// Read from the I2C and NACK
#endif