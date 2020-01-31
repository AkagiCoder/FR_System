#include "I2C.h"

// I2C initialization
void i2c_init(void)
{
	TWSR = 0x00;										// Set prescalar to 0
	TWBR = 0x48;										// SCL = 50 KHz (Fosc = 8 MHz)
	TWCR = (1 << TWEN);									// Enable TWI
}

// Write to the I2C
void i2c_write(unsigned char data)
{
	TWDR = data;										// Data to be transmitted
	TWCR = (1 << TWINT) | (1 << TWEN);					// Use TWI module and write
	while((TWCR & (1 << TWINT)) == 0);					// Wait for TWI to complete
}

// I2C start condition
void i2c_startMT(uint8_t addr)
{
	TWCR = (1 << TWINT) | (1 << TWSTA) | (1 << TWEN);	// Transmit START condition
	while((TWCR & (1 << TWINT)) == 0);					// Wait for TWI to complete
	i2c_write(addr << 1);
}

void i2c_startMR(uint8_t addr)
{
	TWCR = (1 << TWINT) | (1 << TWSTA) | (1 << TWEN);	// Transmit START condition
	while((TWCR & (1 << TWINT)) == 0);					// Wait for TWI to complete
	i2c_write((addr << 1) | 0x01);
}

// I2C stop condition
void i2c_stop(void)
{
	TWCR = (1 << TWINT) | (1 << TWEN) | (1 << TWSTO);	// Transmit STOP condition
}

// Return a byte of data from the I2C and send an ACK
uint8_t i2c_readACK(void)
{
	TWCR = (1 << TWINT) | (1 << TWEN) | (1 << TWEA);
	while((TWCR & (1 << TWINT)) == 0);					// Wait for the data to finish receiving
	return TWDR;										// Return the data
}

// Return a byte of data from the I2C but don't ACK
uint8_t i2c_readNACK(void)
{
	TWCR = (1 << TWINT) | (1 << TWEN);
	while((TWCR & (1 << TWINT)) == 0);
	return TWDR;
}