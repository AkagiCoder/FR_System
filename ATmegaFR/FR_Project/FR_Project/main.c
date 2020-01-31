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

// Rotation of Motor
#define CW		0x00
#define CCW		0x01

// Variables
uint16_t accel[3];					// Acceleration values for all axes
char buffer[10];
uint8_t motorStep = 0;

// Function Declarations
void readAccel();
void motorPortInit();
void rotateMotor(uint8_t dir, uint8_t step);

// Volatile Variables for RX UART interrupt
volatile uint8_t commPos;			// Position of the array of characters [string]
volatile char command[256];			// Commands received from RPi

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
	}
}

ISR(USART_RX_vect)
{
	switch(UDR0)
	{
		// Start of text
		case 2:
			//USART_Print("STX\n\r");
			commPos = -1;
			break;
			
		// End of text
		case 3:
			command[commPos] = UDR0;
			command[commPos+1] = '\0';
			//USART_Print(command);
			//USART_Print("\n\rETX\n\r");
			if(strcmp("RCW", command) == 0)
				rotateMotor(CW, 50);
				//USART_Print("Rotate motor CW\n\r");
			else if(strcmp("RCCW", command) == 0)
				rotateMotor(CCW, 50);
				//USART_Print("Rotate motor CCW\n\r");
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

// Read the MPU6050 acceleration and display to terminal
void readAccel()
{
		MPU_ReadAccel(accel);
		USART_Print("Accelerometer Values:\n\r");
		itoa(accel[0], buffer, 10);
		USART_Print("X: " );
		USART_Print(buffer);
		USART_Print("\n\r");
		itoa(accel[1], buffer, 10);
		USART_Print("Y: " );
		USART_Print(buffer);
		USART_Print("\n\r");
		itoa(accel[2], buffer, 10);
		USART_Print("Z: " );
		USART_Print(buffer);
		USART_Print("\n\r");
}

// Initialize PB1-PD4
void motorPortInit()
{
	DDRB = (0x1E);
	PORTB = 0;				// Output logic zero
}

// Output the logic at PB1-PB4
void rotateMotor(uint8_t dir, uint8_t step)
{
	//uint8_t motorStep = 0;
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
		_delay_ms(10);
	}
	PORTB = 0;		// Cut off PORTB
}