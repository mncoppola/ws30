/*
 * Checksum fixer for Withings WS-30 firmware images
 * (Freescale Kinetis K20 MCU)
 *
 * CRC code directly stolen from http://www.barrgroup.com/Embedded-Systems/How-To/CRC-Calculation-C-Code
 */

#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

#define POLYNOMIAL			0x04C11DB7
#define INITIAL_REMAINDER	0xFFFFFFFF
#define FINAL_XOR_VALUE		0xFFFFFFFF

#define WIDTH    (8 * sizeof(unsigned int))
#define TOPBIT   (1 << (WIDTH - 1))
#define REFLECT_DATA(X)			((unsigned char) reflect((X), 8))
#define REFLECT_REMAINDER(X)	((unsigned int) reflect((X), WIDTH))

struct fw_header {
    unsigned int total_size;
    unsigned int gold;
    unsigned int version;
    unsigned int kinetis_address;
    unsigned int kinetis_size;
    unsigned int kinetis_crc;
    unsigned int wifi_address;
    unsigned int wifi_size;
    unsigned int bluetooth_address;
    unsigned int bluetooth_size;
};

unsigned long reflect ( unsigned long data, unsigned char nBits)
{
	unsigned long reflection = 0x00000000;
	unsigned char bit;

	/*
	 * Reflect the data about the center bit.
	 */
	for (bit = 0; bit < nBits; ++bit)
	{
		/*
		 * If the LSB bit is set, set the reflection of it.
		 */
		if (data & 0x01)
		{
			reflection |= (1 << ((nBits - 1) - bit));
		}

		data = (data >> 1);
	}

	return (reflection);

}	/* reflect() */


unsigned int crcSlow ( unsigned char *message, int nBytes )
{
    unsigned int   remainder = INITIAL_REMAINDER;
	int            byte;
	unsigned char  bit;


    /*
     * Perform modulo-2 division, a byte at a time.
     */
    for (byte = 0; byte < nBytes; ++byte)
    {
        /*
         * Bring the next byte into the remainder.
         */
        remainder ^= (REFLECT_DATA(message[byte]) << (WIDTH - 8));

        /*
         * Perform modulo-2 division, a bit at a time.
         */
        for (bit = 8; bit > 0; --bit)
        {
            /*
             * Try to divide the current data bit.
             */
            if (remainder & TOPBIT)
            {
                remainder = (remainder << 1) ^ POLYNOMIAL;
            }
            else
            {
                remainder = (remainder << 1);
            }
        }
    }

    /*
     * The final remainder is the CRC result.
     */
    return (REFLECT_REMAINDER(remainder) ^ FINAL_XOR_VALUE);

}   /* crcSlow() */

void error ( char *msg )
{
    perror(msg);
    exit(EXIT_FAILURE);
}

int main ( int argc, char **argv )
{
    int fdin, fdout, ret, offset;
    unsigned int image_size, image_crc, kinetis_crc;
    unsigned char *buf;
    struct fw_header *header;

    if ( argc != 2 && argc != 3 )
    {
        printf("Usage: %s <infile> [outfile]\n", argv[0]);
        return -1;
    }

    fdin = open(argv[1], O_RDONLY);
    if ( fdin < 0 )
        error("open");

    ret = read(fdin, &image_size, 4);
    if ( ret < 0 )
        error("error");

    printf("Image is %u bytes\n", image_size);

    lseek(fdin, 0, SEEK_SET);

    buf = malloc(image_size);
    if ( buf == NULL )
        error("malloc");

    offset = 0;
    while ( (ret = read(fdin, buf + offset, image_size - offset)) != 0 )
    {
        if ( ret < 0 )
            error("read");
        offset += ret;
        //printf("Read in %d bytes (%d/%d)\n", ret, offset, image_size);
    }

    header = (struct fw_header *)buf;

    printf("Found WS-30 firmware image:\n");
    printf("    Total size: %u\n", header->total_size);
    printf("    Gold: 0x%08x\n", header->gold);
    printf("    Version: %u\n", header->version);
    printf("    Kinetis address: 0x%x\n", header->kinetis_address);
    printf("    Kinetis size: %u\n", header->kinetis_size);
    printf("    Kinetis CRC: 0x%08x\n", header->kinetis_crc);
    printf("    WiFi address: 0x%x\n", header->wifi_address);
    printf("    WiFi size: %u\n", header->wifi_size);
    printf("    Bluetooth address: 0x%x\n", header->bluetooth_address);
    printf("    Bluetooth size: %u\n", header->bluetooth_size);
    printf("    Image CRC: 0x%08x\n", *(unsigned int *)(buf + header->total_size - 4));

    image_crc = crcSlow(buf, header->total_size - 4);
	printf("\nCalculated image CRC: 0x%08x\n", image_crc);

    kinetis_crc = crcSlow(buf + header->kinetis_address, header->kinetis_size);
    printf("Calculated Kinetis CRC: 0x%08x\n", kinetis_crc);

    close(fdin);

    if ( ! argv[2] )
        return 0;

    if ( header->kinetis_crc != kinetis_crc )
    {
        header->kinetis_crc = kinetis_crc;
        printf("\nPatched Kinetis CRC, recalculating image CRC...\n");

        image_crc = crcSlow(buf, header->total_size - 4);
        printf("Calculated image CRC: 0x%08x\n", image_crc);
    }

    fdout = creat(argv[2], 0666);
    if ( fdout < 0 )
        error("open");

    if ( *(unsigned int *)(buf + header->total_size - 4) != image_crc )
    {
        *(unsigned int *)(buf + header->total_size - 4) = image_crc;
        printf("Patched image CRC\n");
    }

    ret = write(fdout, buf, header->total_size);
    if ( ret < 0 )
        error("write");
    else if ( ret != header->total_size )
    {
        printf("Didn't write out the entire file, try again.\n");
        return -1;
    }

    printf("\nWrote %d bytes to %s\n", ret, argv[2]);

    close(fdout);

    return 0;
}
