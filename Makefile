#---------------------------------------------------------------------------------------------------------------------
# Town Life - Butano project makefile (based on butano/template/Makefile).
# See butano/template/Makefile for documentation of every variable.
#---------------------------------------------------------------------------------------------------------------------
TARGET      	:=  town-life
BUILD       	:=  build
LIBBUTANO   	:=  butano/butano
PYTHON      	:=  python3
SOURCES     	:=  src
INCLUDES    	:=  include butano/common/include
DATA        	:=  data
GRAPHICS    	:=  graphics butano/common/graphics
AUDIO       	:=  audio
AUDIOBACKEND	:=  maxmod
AUDIOTOOL		:=
DMGAUDIO    	:=  dmg_audio
DMGAUDIOBACKEND	:=  default
ROMTITLE    	:=  TOWN LIFE
ROMCODE     	:=  STLE
USERFLAGS   	:=
USERCXXFLAGS	:=
USERASFLAGS 	:=
USERLDFLAGS 	:=
USERLIBDIRS 	:=
USERLIBS    	:=
DEFAULTLIBS 	:=
STACKTRACE		:=
USERBUILD   	:=
EXTTOOL     	:=

#---------------------------------------------------------------------------------------------------------------------
# Export absolute butano path:
#---------------------------------------------------------------------------------------------------------------------
ifndef LIBBUTANOABS
	export LIBBUTANOABS	:=	$(realpath $(LIBBUTANO))
endif

#---------------------------------------------------------------------------------------------------------------------
# Include main makefile:
#---------------------------------------------------------------------------------------------------------------------
include $(LIBBUTANOABS)/butano.mak
