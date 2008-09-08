package sevorg.tic.snippet

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
        case JsonCmd("processForm", _, p: Map[String, String], _) => createActivity(p)
        case x => <tr><td>Didn't understand message! {x}</td></tr>
      })
  }

  private def createActivity(params: Map[String, String]) = {
      val activity = new Activity(urlDecode(params("name")))
      Model.em.persist(activity)
      makeActiveRow(activity)
  }

  def entry = SHtml.jsonForm(json, <head>{JsCmds.Script(json.jsCmd)}</head>
      <input name="name" type="text" />
      <input type="submit" value="Start Activity"/>
    )

  def active: NodeSeq = {
      val activities = Model.em.createQuery("from Activity").getResultList.asInstanceOf[java.util.List[Activity]]
      activities.flatMap(makeActiveRow)
  }

  private def makeActiveRow(act: Activity) = bind("f",
    <tr>
      <td>
        <f:name>Working on tic</f:name>
      </td>
      <td>
        <f:start>10:30</f:start>
      </td>
    </tr>, "name" -> Text(act.getName), "start" -> Text(toInternetDate(act.getStart)))
}
