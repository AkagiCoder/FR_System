#include <stdint.h>
#include <avr/io.h>
#include <stddef.h>
#include <avr/interrupt.h>

#ifndef UART_H_
#define UART_H_
unsigned char USART_Receive(void);
void USART_Init(uint16_t ubrr);
void USART_Transmit(unsigned char data);
void USART_Print(char data[]);
#endif