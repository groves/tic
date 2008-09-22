package sevorg.tic.snippet

import java.text.{ParseException, SimpleDateFormat}
import java.util.{Date, TimeZone}
import scala.xml.{Elem, NodeSeq, Text}

import net.liftweb.http.{JsonCmd, JsonHandler, S, SHtml}
import net.liftweb.http.js.{JsCmd, JsCmds, JsExp, JE}
import JE._
import JsCmds._
import net.liftweb.http.js.jquery.{JqJE, JqJsCmds, JQueryLeft, JQueryRight}
import JqJE._
import JqJsCmds._
import net.liftweb.util.Helpers._

import sevorg.tic.model.{Activity, Model}
import sevorg.tic.model.Model.{setToWrapper,listToWrapper}

class Tic {
  case class JqCSS(name: JsExp, value: JsExp) extends JsExp with JQueryRight with JQueryLeft {
    def toJsCmd = "css(" + name.toJsCmd + ", " + value.toJsCmd + ")"
  }

  val formatter = new SimpleDateFormat("MM/dd HH:mm")
  // TODO - Set a time zone on the user and use it here once users are added and all that
  formatter.setTimeZone(TimeZone.getTimeZone("America/Los_Angeles"))
  object json extends JsonHandler {
    def apply(in: Any) = in match {
        case JsonCmd("processForm", _, p: Map[_, _], _) =>
            createActivity(p.asInstanceOf[Map[String, String]])
        case x => PrependHtml("active", <tr><td>Didn't understand message! {x}</td></tr>)
      }
  }

  private def createActivity(params: Map[String, String]) = {
      val activity = new Activity(urlDecode(params("name")))
      Model.intx {
        Model.em.persist(activity)
      }
      PrependHtml("active", makeRow(activity)) & Jq("#activityname") >> JqAttr("value", "")
  }

  def entry = SHtml.jsonForm(json, <head>{Script(json.jsCmd)}</head>
      <input id="activityname" name="name" type="text" />
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

  def resume(toResume: Activity) = {
      val activity = new Activity(toResume.getName)
      Model.intx {
        Model.em.persist(activity)
      }
      PrependHtml("active", makeRow(activity))
  }

  def delete(toDeleteId: long) = {
    Model.intx {
      val query = Model.em.createQuery("delete from Activity where id = :id")
      query.setParameter("id", toDeleteId).executeUpdate()
    }
    Hide(toDeleteId.toString)
  }

  def changeName(act: Activity)(newName: String) = {
     Model.intx { 
       act.setName(newName)
       Model.em.merge(act)
     }
     true
  }

  def changeStart(act: Activity)(newTime: String): Boolean = {
      val newDate = try {
          formatter.parse(newTime)
      } catch {
          case nfe: ParseException => { return false }
      }
      Model.intx {
          act.setStart(newDate)
          Model.em.merge(act)
      }
      return true
  }

  val Duration = """(\d+)(h|m)""".r
  val minute = 60 * 1000
  val hour = 60 * minute
  def changeDuration(act: Activity)(newDuration: String): Boolean = {
      val milliduration = (0 /: ((Duration findAllIn newDuration) map (_ match {
          case Duration(value, "h") => Integer.parseInt(value) * hour
          case Duration(value, "m") => Integer.parseInt(value) * minute
      })))(_ + _)
      Model.intx {
          act.setStop(new Date(act.getStart.getTime + milliduration))
          Model.em.merge(act)
      }
      return true
  }

  private def byId(id: long) = {
    val query = Model.em.createQuery("SELECT a FROM Activity a WHERE a.id = :id")
    query.setParameter("id", id).getSingleResult.asInstanceOf[Activity]
  }

  private def duration(act: Activity) = {
      val millis = act.getStop.getTime - act.getStart.getTime
      val hours = millis / hour
      val minutes = millis % hour / minute
      <td>{ validatingSwappable(hours + "h " + minutes + "m", changeDuration(act)) }</td>
  }

  def validatingSwappable(initialValue: String, validator: String => Boolean) = {
      val (rs, shownId) = findOrAddId(<span>{initialValue}</span>)
      val hiddenId = "R" + randomString(12)
      def swapOrShowError(restoreJS: String)(newValue: String):JsCmd = {
          if(validator(newValue)){
              JsRaw(restoreJS) & Jq("#" + shownId) >> JqText(newValue)
          } else {
              Jq("#" + hiddenId + ":first-child") >> JqCSS("border", "solid red 1px")
          }
      }
      SHtml.swappable(rs, (restoreJS: String) =>{
              <span id={hiddenId}>{SHtml.ajaxText(initialValue, swapOrShowError(restoreJS))}</span> })
  }

  private def makeRow(act: Activity): NodeSeq = {
    <tr id={ Text(act.getId.toString) }>
      <td>{ validatingSwappable(act.getName, changeName(act)) }</td>
      <td>{ validatingSwappable(formatter.format(act.getStart), changeStart(act)) }</td>
      { if (act.getStop != null) duration(act) else NodeSeq.Empty }
      <td>{  if (act.getStop == null) {
                 SHtml.a(() => {stop(act)}, Text("Stop"))
             } else {
                 SHtml.a(() => {resume(act)}, Text("Resume"))
             }
          }
      </td>
      <td> { SHtml.a(() => {delete(act.getId)}, Text("Delete")) }</td>
    </tr>
  }
}
