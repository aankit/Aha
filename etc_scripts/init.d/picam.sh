#! /bin/sh
### BEGIN INIT INFO
# Provides:          picam
# Required-Start:    $ALL
# Required-Stop:     $ALL
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: picam
### END INIT INFO

#
# Author: Emanuel Kuehnel <emanuel@kcdesign.de>
#         Nao Iizuka <iizuka@kyu-mu.net>
#

PATH=/sbin:/usr/sbin:/bin:/usr/bin
DESC="picam"
NAME="picam"
RAM_DIR="/run/shm"
PICAM_DIR="/home/pi/picam"
PICAM_COMMAND="$PICAM_DIR/picam"
UGID="pi:pi"
SCRIPTNAME=/etc/init.d/$NAME
START_PICAM=false
CONFIG_FILE=/etc/default/$NAME

# Read configuration variable file if it is present
[ -r $CONFIG_FILE ] && . $CONFIG_FILE

# Load the VERBOSE setting and other rcS variables
. /lib/init/vars.sh

# Define LSB log_* functions.
# Depend on lsb-base (>= 3.2-14) to ensure that this file is present
# and status_of_proc is working.
. /lib/lsb/init-functions

# Check if $PICAM_DIR is accessible
if [ ! -d "$PICAM_DIR" ] || [ ! -x "$PICAM_DIR" ]; then
  echo "Error: $PICAM_DIR is not accessible"
  echo "Hint: Set PICAM_DIR in $CONFIG_FILE"
  exit 1
fi

# Compose command line options
PICAM_OPTIONS="--quiet \
  --fps $VIDEO_FRAMERATE \
  --width $VIDEO_WIDTH \
  --height $VIDEO_HEIGHT \
  --rotation $VIDEO_ROTATION \
  --videobitrate $VIDEO_BITRATE \
  --qpmin $VIDEO_QPMIN \
  --qpmax $VIDEO_QPMAX \
  --qpinit $VIDEO_QPINIT \
  --alsadev $ALSADEV \
  $OTHER_OPTIONS"
if [ "$ENABLE_HLS" = "true" ]; then
  PICAM_OPTIONS="$PICAM_OPTIONS --hlsdir $HLS_DIR"
  if [ "$ENABLE_HLS_ENCRYPTION" = "true" ]; then
    PICAM_OPTIONS="$PICAM_OPTIONS --hlsenc \
      --hlsenckeyuri $HLS_ENCRYPTION_KEY_FILE \
      --hlsenckey $HLS_ENCRYPTION_KEY \
      --hlsenciv $HLS_ENCRYPTION_IV"
  fi
fi
if [ "$VIDEO_HORIZONTAL_FLIP" = "true" ]; then
  PICAM_OPTIONS="$PICAM_OPTIONS --hflip"
fi
if [ "$VIDEO_VERTICAL_FLIP" = "true" ]; then
  PICAM_OPTIONS="$PICAM_OPTIONS --vflip"
fi
if [ "$ENABLE_AUDIO" = "false" ]; then
  PICAM_OPTIONS="$PICAM_OPTIONS --noaudio"
fi

#
# Function that starts the daemon/service
#
do_start()
{
  if [ $START_PICAM = "true" ]; then
    # Create hooks dir and set permission
    if [ ! -d $RAM_DIR/hooks ]; then
      echo "creating $RAM_DIR/hooks directory"
      mkdir -p $RAM_DIR/hooks
    fi
    if [ -d $RAM_DIR/hooks ]; then
      chown -R $UGID $RAM_DIR/hooks
    else
      echo "Error: failed to create $RAM_DIR/hooks"
      exit 1
    fi

    # Create state dir and set permission
    if [ ! -d $RAM_DIR/state ]; then
      echo "creating $RAM_DIR/state directory"
      mkdir -p $RAM_DIR/state
    fi
    if [ -d $RAM_DIR/state ]; then
      chown -R $UGID $RAM_DIR/state
    else
      echo "Error: failed to create $RAM_DIR/state"
      exit 1
    fi

    # Create rec dir and set permission
    if [ ! -d $RAM_DIR/rec ]; then
      echo "creating $RAM_DIR/rec directory"
      mkdir -p $RAM_DIR/rec
    fi
    if [ -d $RAM_DIR/rec ]; then
      chown -R $UGID $RAM_DIR/rec
    else
      echo "Error: failed to create $RAM_DIR/rec"
      exit 1
    fi

    # Create SD card archive and set permission
    if [ ! -d $PICAM_DIR/archive ]; then
      echo "creating $PICAM_DIR/archive directory"
      mkdir -p $PICAM_DIR/archive
    fi
    if [ -d $PICAM_DIR/archive ]; then
      chown -R $UGID $PICAM_DIR/archive
    else
      echo "Error: failed to create $PICAM_DIR/archive"
      exit 1
    fi
    
    #make symlink from RAM to SD card archive and set permission
    if [ ! -h $RAM_DIR/rec/archive ]; then
      echo "creating $PICAM_DIR/archive directory"
      ln -s $PICAM_DIR/archive $RAM_DIR/rec/archive
    fi
    if [ -h $RAM_DIR/rec/archive ]; then
      chown -R $UGID $RAM_DIR/rec/archive
    else
      echo "Error: failed to create $RAM_DIR/rec"
      exit 1
    fi

    if [ "$ENABLE_HLS" = "true" ]; then
      if [ ! -d $HLS_DIR ]; then
        echo "creating $HLS_DIR directory"
        mkdir -p $HLS_DIR
      fi
      # Correct permissions for $HLS_DIR
      if [ -d $HLS_DIR ]; then
        chown -R $UGID $HLS_DIR
      else
        echo "Error: failed to create $HLS_DIR"
        exit 1
      fi

      if [ "$ENABLE_HLS_ENCRYPTION" = "true" ] && [ "$HLS_CREATE_ENCRYPTION_KEY_FILE" = "true" ]; then
        # Create encryption key file
        printf "$HLS_ENCRYPTION_KEY" | \
          perl -ne 'print pack "H*", $_' > $HLS_DIR"/"$HLS_ENCRYPTION_KEY_FILE
      fi
      [ -f $HLS_DIR"/"$HLS_ENCRYPTION_KEY_FILE ] && chown $UGID $HLS_DIR"/"$HLS_ENCRYPTION_KEY_FILE
    fi

    # Exit if picam is not executable
    [ -x "$PICAM_COMMAND" ] || {
      echo "Error: $PICAM_COMMAND is not executable"
      echo "Hint: Set PICAM_COMMAND in $CONFIG_FILE"
      exit 1
    }

    # Return
    #   0 if daemon has been started
    #   1 if daemon was already running
    #   2 if daemon could not be started
    start-stop-daemon \
      --start \
      --pidfile $PIDFILE \
      --chuid $UGID \
      --exec $PICAM_COMMAND \
      --test \
      > /dev/null \
      || return 1
    ( start-stop-daemon \
      --start \
      --background \
      --make-pidfile \
      --pidfile $PIDFILE \
      --chuid $UGID \
      --chdir $PICAM_DIR \
      --exec $PICAM_COMMAND \
      -- $PICAM_OPTIONS ) \
    || return 2
  else
    echo "service disabled in $CONFIG_FILE"
  fi
}

#
# Function that stops the daemon/service
#
do_stop()
{
  # Return
  #   0 if daemon has been stopped
  #   1 if daemon was already stopped
  #   2 if daemon could not be stopped
  #   other if a failure occurred
  start-stop-daemon --stop --retry=TERM/10/KILL/5 --pidfile $PIDFILE --name $NAME
  RETVAL="$?"
  [ "$RETVAL" = 2 ] && return 2
  # Many daemons don't delete their pidfiles when they exit.
  [ -f $PIDFILE ] && rm -f $PIDFILE

  # Delete HLS files
  if [ "$ENABLE_HLS" = "true" ]; then
    find $HLS_DIR -name *.ts -exec rm {} \;
    [ -f $HLS_DIR/index.m3u8 ] && rm $HLS_DIR/index.m3u8
    if [ "$HLS_CREATE_ENCRYPTION_KEY_FILE" = "true" ]; then
      [ -f $HLS_DIR/$HLS_ENCRYPTION_KEY_FILE ] && rm $HLS_DIR/$HLS_ENCRYPTION_KEY_FILE
    fi
  fi

  return "$RETVAL"
}

case "$1" in
  start)
  [ "$VERBOSE" != no ] && log_daemon_msg "Starting $DESC" "$NAME"
  do_start
  case "$?" in
    0|1) [ "$VERBOSE" != no ] && log_end_msg 0 ;;
    2) [ "$VERBOSE" != no ] && log_end_msg 1 ;;
  esac
  ;;
  stop)
  [ "$VERBOSE" != no ] && log_daemon_msg "Stopping $DESC" "$NAME"
  do_stop
  case "$?" in
    0|1) [ "$VERBOSE" != no ] && log_end_msg 0 ;;
    2) [ "$VERBOSE" != no ] && log_end_msg 1 ;;
  esac
  ;;
  status)
  status_of_proc "$PICAM_COMMAND" "$NAME" && exit 0 || exit $?
  ;;
  restart)
  #
  # If the "reload" option is implemented then remove the
  # 'force-reload' alias
  #
  log_daemon_msg "Restarting $DESC" "$NAME"
  do_stop
  case "$?" in
    0|1)
    do_start
    case "$?" in
      0) log_end_msg 0 ;;
      1) log_end_msg 1 ;; # Old process is still running
      *) log_end_msg 1 ;; # Failed to start
    esac
    ;;
    *)
    # Failed to stop
    log_end_msg 1
    ;;
  esac
  ;;
  *)
  echo "Usage: $SCRIPTNAME {start|stop|status|restart}" >&2
  exit 3
  ;;
esac

exit 0