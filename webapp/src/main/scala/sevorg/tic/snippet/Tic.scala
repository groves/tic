package sevorg.tic.snippet

import java.text.SimpleDateFormat
import scala.xml.{NodeSeq, Text}

import net.liftweb.http.{JsonCmd, JsonHandler, S, SHtml}
import net.liftweb.http.js.{JsCmd, JsCmds, JE}
import JE._
import JsCmds._
import net.liftweb.http.js.jquery.{JqJE, JqJsCmds}
import JqJE._
import JqJsCmds._
import net.liftweb.util.Helpers._

import sevorg.tic.model.{Activity, Model}
import sevorg.tic.model.Model.{setToWrapper,listToWrapper}

class Tic {
  val formatter = new SimpleDateFormat("MM/dd HH:mm")
  object json extends JsonHandler {
    def apply(in: Any): JsCmd = PrependHtml("active", in match {
        case JsonCmd("processForm", _, p: Map[_, _], _) =>
            createActivity(p.asInstanceOf[Map[String, String]])
        case x => <tr><td>Didn't understand message! {x}</td></tr>
      })
  }

  private def createActivity(params: Map[String, String]) = {
      val activity = new Activity(urlDecode(params("name")))
      Model.intx {
        Model.em.persist(activity)
      }
      makeRow(activity)
  }

  def entry = SHtml.jsonForm(json, <head>{Script(json.jsCmd)}</head>
      <input name="name" type="text" />
      <input type="submit" value="Start"/>)

  def active: NodeSeq = all("a.stop is null").flatMap(makeRow)

  def inactive: NodeSeq = all("a.stop is not null").flatMap(makeRow)

  private def all(clause: String) =  {
      val query = Model.em.createQuery("select a from Activity a where " + clause + " order by a.start desc")
      query.getResultList.asInstanceOf[java.util.List[Activity]]
  }

  def stop(toStop: Activity) = {
      Model.intx {
        toStop.stop()
        Model.em.merge(toStop)
      }
      Hide(toStop.getId.toString) & PrependHtml("inactive", makeRow(toStop))
  }

  def restart(toRestart: Activity) = {
      Model.intx {
        toRestart.setStop(null)
        Model.em.merge(toRestart)
      }
      Hide(toRestart.getId.toString) & PrependHtml("active", makeRow(toRestart))
  }

  def delete(toDeleteId: long) = {
    Model.intx {
      val query = Model.em.createQuery("delete from Activity where id = :id")
      query.setParameter("id", toDeleteId).executeUpdate()
    }
    Hide(toDeleteId.toString)
  }

  def changeName(act: Activity, newName: String) = {
     Model.intx { 
       act.setName(newName)
       Model.em.merge(act)
     }
     Jq("#" + act.getId + " td:first-child span span") >> JqText(newName)
  }

  def changeStart(act: Activity, newTime: String) = {
      val newDate = formatter.parse(newTime)
      Model.intx {
          act.setStart(newDate)
          Model.em.merge(act)
      }
      Jq("#" + act.getId + " td:eq(1) span span") >> JqText(formatter.format(newDate))
  }

  private def byId(id: long) = {
    val query = Model.em.createQuery("SELECT a FROM Activity a WHERE a.id = :id")
    query.setParameter("id", id).getSingleResult.asInstanceOf[Activity]
  }

  val minute = 60 * 1000
  val hour = 60 * minute
  private def duration(act: Activity) = {
      val millis = act.getStop.getTime - act.getStart.getTime
      val hours = millis / hour
      val minutes = millis % hour / minute
      <td>{ hours + "h " + minutes + "m" }</td>
  }

  private def makeRow(act: Activity): NodeSeq = {
    <tr id={ Text(act.getId.toString) }>
      <td>{ SHtml.swappable(<span>{ act.getName }</span>,
                            SHtml.ajaxText(act.getName, v => changeName(act, v))) }
      </td>
      <td>{ SHtml.swappable(<span>{ formatter.format(act.getStart) }</span>,
                            SHtml.ajaxText(formatter.format(act.getStart),
                                           v => changeStart(act, v)))
          }
      </td>
      { if (act.getStop != null) duration(act) else NodeSeq.Empty }
      <td> {  if (act.getStop == null) {
                  SHtml.a(() => {stop(act)}, Text("Stop"))
              } else {
                  SHtml.a(() => {restart(act)}, Text("Restart"))
              }
          }
      </td>
      <td> { SHtml.a(() => {delete(act.getId)}, Text("Delete")) }</td>
    </tr>
  }
}
