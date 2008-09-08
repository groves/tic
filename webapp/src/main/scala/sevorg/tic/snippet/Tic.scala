package sevorg.tic.snippet

import java.text.SimpleDateFormat
import scala.xml.{Group, NodeSeq, Text}

import net.liftweb.http.{JsonCmd, JsonHandler, S, SHtml}
import net.liftweb.http.js.{JsCmd, JsCmds}
import net.liftweb.http.js.jquery.JqJsCmds
import net.liftweb.util.Helpers._

import sevorg.tic.model.{Activity, Model}
import sevorg.tic.model.Model.{setToWrapper,listToWrapper}

class Tic {
  object json extends JsonHandler {
    def apply(in: Any): JsCmd = JqJsCmds.PrependHtml("active", in match {
        case JsonCmd("processForm", _, p: Map[_, _], _) => createActivity(p.asInstanceOf[Map[String, String]])
        case x => <tr><td>Didn't understand message! {x}</td></tr>
      })
  }

  private def createActivity(params: Map[String, String]) = {
      val activity = new Activity(urlDecode(params("name")))
      intransaction { Model.em.persist(activity) }
      makeRow(activity)
  }

  def entry = SHtml.jsonForm(json, <head>{JsCmds.Script(json.jsCmd)}</head>
      <input name="name" type="text" />
      <input type="submit" value="Start Activity"/>
    )

  def active: NodeSeq = {
      val activities = Model.em.createQuery("SELECT a FROM Activity a WHERE a.stop IS NULL").getResultList.asInstanceOf[java.util.List[Activity]]
      activities.flatMap(makeRow)
  }

  def inactive: NodeSeq = {
      val activities = Model.em.createQuery("SELECT a FROM Activity a WHERE a.stop IS NOT NULL").getResultList.asInstanceOf[java.util.List[Activity]]
      activities.flatMap(makeRow)
  }

  def stop(id: long) = {
      val ending = byId(id)
      intransaction { ending.stop(); Model.em.merge(ending) }
      JqJsCmds.Hide(id.toString) & JqJsCmds.PrependHtml("inactive", makeRow(ending))
  }

  def restart(id: long) = {
      val restarting = byId(id)
      intransaction { restarting.setStop(null); Model.em.merge(restarting) }
      JqJsCmds.Hide(id.toString) & JqJsCmds.PrependHtml("active", makeRow(restarting))
  }

  private def intransaction(f: Unit) = {
    val tran = Model.em.getTransaction()
    tran.begin()
    f
    tran.commit()
  }

  private def byId(id: long) = Model.em.createQuery("SELECT a FROM Activity a WHERE a.id = :id").setParameter("id", id).getSingleResult.asInstanceOf[Activity]

  val todayFormatter = new SimpleDateFormat("HH:mm")
  val earlierFormatter = new SimpleDateFormat("MM/dd HH:mm")
  private def makeRow(act: Activity): NodeSeq = {
    val formatter = if (System.currentTimeMillis - act.getStart.getTime < (1000 * 60 * 60 * 24)) todayFormatter else earlierFormatter
    bind("f",
      <tr id={Text(act.getId.toString)}>
        <td>
          <f:name>Working on tic</f:name>
        </td>
        <td>
          <f:start>10:30</f:start>
        </td>
        <td>
          { if(act.getStop == null) SHtml.a(() => {stop(act.getId)}, Text("Stop"))
            else SHtml.a(() => {restart(act.getId)}, Text("Restart"))
          }
        </td>
      </tr>, "name" -> Text(act.getName), "start" -> Text(formatter.format(act.getStart)))
  }
}
