#include "USART.h"

unsigned char USART_Receive(void)
{
	while(!(UCSR0A & (1 << RXC0)));
	return UDR0;
}

void USART_Init(uint16_t ubrr)
{
	// Set baud rate
	UBRR0H = (uint8_t)(ubrr >> 8);
	UBRR0L = (uint8_t) ubrr;
	// Enable receiver and transmitter; Enable RX interrupt
	UCSR0B = (1 << RXEN0) | (1 << TXEN0) | (1 << RXCIE0);
	// Set frame format: 1 byte of data, 1 stop bits
	UCSR0C = (3 << UCSZ00);
}

void USART_Transmit(unsigned char data)
{
	// Wait for empty transfer buffer
	while(!(UCSR0A & (1 << UDRE0)));
	UDR0 = data;
}

void USART_Print(char data [])
{
	int i = 0;
	do 
	{
		USART_Transmit(data[i]);
		i++;
	} while (data[i] != '\0');
}

