package sevorg.tic.model

import net.liftweb.mapper.{KeyedMapper, KeyedMetaMapper, MappedLong, MappedLongIndex, MappedString}
import net.liftweb.util.Helpers

/**
* The singleton that has methods for accessing the database
*/
trait MetaActivity extends Activity with KeyedMetaMapper[long, Activity]
object Activity extends MetaActivity {
 override def dbTableName = "activity" // define the DB table name

 // define the order fields will appear in forms and output
 override def fieldOrder =  List(id, name, start, end)
}

class Activity extends KeyedMapper[Long, Activity] {
  def getSingleton = Activity
  def primaryKeyField = id

  object id extends MappedLongIndex(this)

  object name extends MappedString(this, 255) {
    override def dbIndexed_? = true
  }

  object start extends MappedLong(this) {
     override def defaultValue = System.currentTimeMillis
  }

  object end extends MappedLong(this)
}
