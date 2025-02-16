bind pub -|- !bwrecord bwrecord
proc bwrecord {nick uhost hand chan args} {
   set bwrecord {/mnt/glftpd/bin/bwrecord/bw_record_query.py}
   catch {set msgthis [exec python3 $bwrecord]} msgthis
   foreach line [split $msgthis \n] {
	putquick "PRIVMSG $chan : $line"
  }
}