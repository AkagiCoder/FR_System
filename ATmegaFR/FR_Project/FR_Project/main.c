#define F_CPU 16000000UL

#include <avr/io.h>
#include <stdint.h>
#include <util/delay.h>
#include <stdlib.h>
#include <string.h>
#include "I2C.h"
#include "MPU6050.h"
#include "USART.h"

// Macros
#define FOSC	16000000UL			// ATmega clock frequency
#define BAUD	9600
#define MYUBRR	FOSC/16/BAUD-1		// Asynchronous normal mode

// Motor Position
#define BLK		0x02
#define GRN		0x04
#define RED		0x08
#define BLU		0x10

// Axis of MPU
#define X_Axis	0x00
#define Y_Axis	0x01
#define Z_Axis	0x02

// Rotation of Motor
#define CW		0x00
#define CCW		0x01

// Variables
uint16_t accel[3];					// Acceleration values for all axes
char buffer[10];
volatile uint8_t motorStep = 0;

// Function Declarations
void motorPortInit();
void rotateMotor(uint8_t dir, uint8_t step);
//void MPU_UART(uint8_t axis);
void MPU_UART();

// Volatile Variables for RX UART interrupt
volatile uint8_t commPos;			// Position of the array of characters [string]
char command[256];			// Commands received from RPi

int main(void)
{	
	commPos = 0;
	i2c_init();				// Initialize I2C module
	USART_Init(MYUBRR);		// Initialize USART module
	MPU_init();				// Wake up MPU6050
	motorPortInit();		// Initialize PD2-PD5 for stepper motor

	sei();

	while(1)
	{
		/*
		MPU_ReadAccel(accel);
		itoa(accel[X_Axis], buffer, 10);
		USART_Print("X: ");
		USART_Print(buffer);
		USART_Print("\r\n");
		itoa(accel[Y_Axis], buffer, 10);
		USART_Print("Y: ");
		USART_Print(buffer);
		USART_Print("\r\n");
		itoa(accel[Z_Axis], buffer, 10);
		USART_Print("Z: ");
		USART_Print(buffer);
		USART_Print("\r\n\r\n");
		_delay_ms(200);
		*/
	}
}

// Commands received from the UART are processed here
// [COMMANDS]	[Action]
// RCW			Rotate motor clockwise
// RCCW			Rotate motor counter-clockwise
// ACCEL_X		Get the acceleration on the X-axis
// ACCEL_Y		Get the acceleration on the Y-axis
// ACCEL_Z		Get the acceleration on the Z-axis
ISR(USART_RX_vect)
{
	switch(UDR0)
	{
		// Start of text (STX)
		case 2:
			commPos = -1;
			break;
			
		// End of text (ETX)
		case 3:
			command[commPos] = UDR0;
			command[commPos+1] = '\0';
			
			// Rotate motor clockwise
			if(strcmp("RCW", command) == 0)
				rotateMotor(CW, 50);
			// Rotate motor counter-clockwise
			else if(strcmp("RCCW", command) == 0)
				rotateMotor(CCW, 50);
			// Retrieve value from MPU accelerometer on the X-axis
			/*
			else if(strcmp("ACCEL_X", command) == 0)
				MPU_UART(X_Axis);
			else if(strcmp("ACCEL_Y", command) == 0)
				MPU_UART(Y_Axis);
			else if(strcmp("ACCEL_Z", command) == 0)
				MPU_UART(Z_Axis);
			break;
			*/
			else if(strcmp("ACCEL", command) == 0)
				MPU_UART();
			break;
			
		default:
			if(commPos >= 0)
				command[commPos] = UDR0;
			commPos++;
			// Prevent overflow to the command buffer
			if(commPos > 254)
			{
				commPos = -1;
				USART_Print("ERROR: Buffer overflow\n\r");
			}
			
	}
}

// Initialize PB1-PD4
void motorPortInit()
{
	DDRB = (0x1E);
	PORTB = 0;				// Set PB output to zero
}

// Rotate the motor on PB1-PB4
// Specify the direction and # of steps
void rotateMotor(uint8_t dir, uint8_t step)
{
	for(int i = 0; i <= step; i++)
	{
		// Rotate CW
		if(dir == CW)
		{
			if(motorStep >= 3)
				motorStep = 0;
			else
				motorStep++;
		}
		// Rotate CCW
		else
		{
			if(motorStep <= 0)
				motorStep = 3;
			else
				motorStep--;
		}
		switch(motorStep)
		{
			case 0:
				PORTB = BLK | RED;
				break;
			case 1:
				PORTB = RED | GRN;
				break;
			case 2:
				PORTB = GRN | BLU;
				break;
			case 3:
				PORTB = BLU | BLK;
				break;
		}
		_delay_ms(10);	// Delay required for the motor to step through
	}
	PORTB = 0;		// Cut off PORTB
}

// Sends the read acceleration value of a particular axis through UART
/*
void MPU_UART(uint8_t axis)
{
	MPU_ReadAccel(accel);
	itoa(accel[axis], buffer, 10);
	USART_Print(buffer);
	USART_Print("\n");
}
*/
void MPU_UART()
{
	MPU_ReadAccel(accel);
	// Send X, Y, and Z acceleration
	for(int i = 0; i < 3; i++)
	{
		itoa(accel[i], buffer, 10);
		USART_Print(buffer);
		USART_Print(" ");
	}
	// EOL
	USART_Print("\n");
}