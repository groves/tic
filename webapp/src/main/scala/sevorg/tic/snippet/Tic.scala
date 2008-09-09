package sevorg.tic.snippet

import java.text.SimpleDateFormat
import scala.xml.{NodeSeq, Text}

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
      Model.intx { Model.em.persist(activity) }
      makeRow(activity)
  }

  def entry = SHtml.jsonForm(json, <head>{JsCmds.Script(json.jsCmd)}</head>
      <input name="name" type="text" />
      <input type="submit" value="Start Activity"/>)

  def active: NodeSeq = all("a.stop is null").flatMap(makeRow)

  def inactive: NodeSeq = all("a.stop is not null").flatMap(makeRow)

  private def all(clause: String) =  {
      val query = Model.em.createQuery("select a from Activity a where " + clause + " order by a.start desc")
      query.getResultList.asInstanceOf[java.util.List[Activity]]
  }

  def stop(toStop: Activity) = {
      Model.intx { toStop.stop(); Model.em.merge(toStop) }
      JqJsCmds.Hide(toStop.getId.toString) & JqJsCmds.PrependHtml("inactive", makeRow(toStop))
  }

  def restart(toRestart: Activity) = {
      Model.intx { toRestart.setStop(null); Model.em.merge(toRestart) }
      JqJsCmds.Hide(toRestart.getId.toString) & JqJsCmds.PrependHtml("active", makeRow(toRestart))
  }

  def delete(toDeleteId: long) = {
    Model.intx { Model.em.createQuery("delete from Activity where id = :id").setParameter("id", toDeleteId).executeUpdate() }
    JqJsCmds.Hide(toDeleteId.toString)
  }


  private def byId(id: long) = Model.em.createQuery("SELECT a FROM Activity a WHERE a.id = :id").setParameter("id", id).getSingleResult.asInstanceOf[Activity]

  val minute = 60 * 1000
  val hour = 60 * minute
  private def duration(act: Activity) = {
      val millis = act.getStop.getTime - act.getStart.getTime
      val hours = millis / hour
      val minutes = millis % hour / minute
      <td>{ hours + "h " + minutes + "m" }</td>
  }

  val formatter = new SimpleDateFormat("MM/dd HH:mm")
  private def makeRow(act: Activity): NodeSeq = {
    <tr id={ Text(act.getId.toString) }>
      <td>{ Text(act.getName) }</td>
      <td>{ formatter.format(act.getStart) }</td>
      { if (act.getStop != null) duration(act) else NodeSeq.Empty }
      <td> { if (act.getStop == null) SHtml.a(() => {stop(act)}, Text("Stop")) else SHtml.a(() => {restart(act)}, Text("Restart")) }</td>
      <td> { SHtml.a(() => {delete(act.getId)}, Text("Delete"))  }</td>
    </tr>
  }
}
